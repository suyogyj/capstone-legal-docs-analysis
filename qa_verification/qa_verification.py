#!/usr/bin/env python3
"""
Q/A-based Verification Script for Indian Court Judgments
This script processes court judgment PDFs, asks each document a set of questions 
(with rephrased variants), and records the answers to evaluate consistency.
"""

import os
import re
import csv
import json
import time
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd
from tqdm import tqdm
import PyPDF2
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import tiktoken

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("qa_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("qa_verification")

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process court judgment PDFs and perform Q&A verification.")
    
    parser.add_argument(
        "--input-csv", 
        required=True, 
        help="Path to CSV file containing questions and their rephrased variants"
    )
    parser.add_argument(
        "--pdf-dir", 
        required=True, 
        help="Directory containing PDF files of court judgments"
    )
    parser.add_argument(
        "--output-csv", 
        required=True, 
        help="Path where the output CSV will be saved"
    )
    parser.add_argument(
        "--output-json", 
        help="Optional path where detailed JSON analytics will be saved"
    )
    parser.add_argument(
        "--model", 
        default="gpt-4o-mini", 
        help="OpenAI model to use for queries (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30, 
        help="Timeout for LLM requests in seconds (default: 30)"
    )
    parser.add_argument(
        "--max-tokens", 
        type=int, 
        default=8192, 
        help="Maximum number of tokens to process from each PDF (default: 8192)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def read_questions_csv(filepath: str) -> pd.DataFrame:
    """
    Read the CSV file containing questions and their rephrased variants.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing questions and their rephrased variants
    """
    logger.info(f"Reading questions from {filepath}")
    try:
        df = pd.read_csv(filepath)
        
        # Ensure the CSV has the required structure
        # At minimum, we need question_id, question, and three rephrases
        required_columns = ["question_id", "question"]
        for i in range(1, 4):
            required_columns.append(f"rephrase{i}")
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")
        
        logger.info(f"Successfully loaded {len(df)} questions")
        return df
    except Exception as e:
        logger.error(f"Error reading questions CSV: {str(e)}")
        raise

def extract_text_from_pdf(pdf_path: str, max_tokens: int = 8192) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        max_tokens: Maximum number of tokens to extract (to avoid hitting LLM context limits)
        
    Returns:
        Extracted text from the PDF
    """
    logger.debug(f"Extracting text from {pdf_path}")
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text()
                
            # Clean the text - remove references to Indian Kanoon and other common artifacts
            text = re.sub(r'Indian Kanoon - http://indiankanoon.org/doc/\d+/ \d', '', text)
            text = re.sub(r'http://www.judis.nic.in', '', text)
            
            # Truncate to max_tokens if needed
            encoding = tiktoken.encoding_for_model("gpt-4o-mini")
            tokens = encoding.encode(text)
            if len(tokens) > max_tokens:
                logger.debug(f"Truncating text from {len(tokens)} to {max_tokens} tokens")
                text = encoding.decode(tokens[:max_tokens])
            
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        raise

def extract_case_name(pdf_filename: str) -> str:
    """
    Extract the case name from the PDF filename.
    
    Args:
        pdf_filename: Name of the PDF file
        
    Returns:
        Extracted case name
    """
    case_name = os.path.splitext(pdf_filename)[0]
    return case_name

def query_llm_original(text: str, question: str, model: str, timeout: int) -> Dict[str, Any]:
    """
    Query the LLM with the original question about the text.
    
    Args:
        text: The text to analyze (PDF content)
        question: The question to ask
        model: The OpenAI model to use
        timeout: Timeout for the request in seconds
        
    Returns:
        Dictionary containing the answer and metadata
    """
    start_time = time.time()
    
    try:
        # Create LangChain ChatOpenAI instance
        chat = ChatOpenAI(
            model_name=model,
            temperature=0,
            request_timeout=timeout
        )
        
        # Prepare the prompt for original question
        prompt = f"""You are an expert legal assistant. Here is an excerpt from an Indian court judgment:

{text}

Answer the following question:
{question}

Provide a concise and specific answer that references relevant parts of the judgment. 
Your answer should be brief but accurate. If the information is not available, state "Not specified".
"""

        # Send the query to the LLM
        messages = [HumanMessage(content=prompt)]
        response = chat(messages)
        
        # Calculate duration
        duration = time.time() - start_time
        
        return {
            "answer": response.content,
            "duration": duration,
            "status": "success"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error querying LLM with original question: {str(e)}")
        return {
            "answer": f"Error: {str(e)}",
            "duration": duration,
            "status": "error",
            "error": str(e)
        }

def query_llm_verification(text: str, original_answer: str, rephrased_question: str, model: str, timeout: int) -> Dict[str, Any]:
    """
    Query the LLM with a verification question that incorporates the original answer.
    
    Args:
        text: The text to analyze (PDF content)
        original_answer: The answer from the original question
        rephrased_question: The template for the rephrased question
        model: The OpenAI model to use
        timeout: Timeout for the request in seconds
        
    Returns:
        Dictionary containing the verification result and metadata
    """
    start_time = time.time()
    
    try:
        # Create LangChain ChatOpenAI instance
        chat = ChatOpenAI(
            model_name=model,
            temperature=0,
            request_timeout=timeout
        )
        
        # Insert the original answer into the rephrased question
        verification_statement = rephrased_question.format(answer=original_answer)
        
        # Prepare the prompt for verification
        prompt = f"""You are an expert legal assistant. Here is an excerpt from an Indian court judgment:

{text}

Based on the judgment, please verify if the following statement is correct:
"{verification_statement}"

If the statement is correct, respond with "Correct". 
If the statement is incorrect, respond with "Incorrect" followed by the correct information.
If the information cannot be verified from the judgment, respond with "Cannot verify".
"""

        # Send the query to the LLM
        messages = [HumanMessage(content=prompt)]
        response = chat(messages)
        
        # Calculate duration
        duration = time.time() - start_time
        
        return {
            "verification": response.content,
            "duration": duration,
            "status": "success"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error querying LLM with verification question: {str(e)}")
        return {
            "verification": f"Error: {str(e)}",
            "duration": duration,
            "status": "error",
            "error": str(e)
        }

def process_pdf(pdf_path: str, questions_df: pd.DataFrame, args: argparse.Namespace) -> List[Dict[str, Any]]:
    """
    Process a single PDF file - extract text and query the LLM with each question variant.
    
    Args:
        pdf_path: Path to the PDF file
        questions_df: DataFrame containing questions and their rephrased variants
        args: Command line arguments
        
    Returns:
        List of dictionaries containing results for each question
    """
    results = []
    case_name = extract_case_name(os.path.basename(pdf_path))
    logger.info(f"Processing case: {case_name}")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path, args.max_tokens)
        
        # Process each question and its rephrased variants
        for _, row in tqdm(questions_df.iterrows(), total=len(questions_df), desc=f"Processing questions for {case_name}"):
            question_id = row['question_id']
            original_question = row['question']
            
            question_result = {
                "case_name": case_name,
                "question_id": question_id,
                "original_question": original_question,
                "pdf_path": pdf_path,
                "timestamp": datetime.now().isoformat()
            }
            
            # First, get the answer to the original question
            logger.debug(f"Processing original question {question_id}: {original_question}")
            original_response = query_llm_original(text, original_question, args.model, args.timeout)
            
            question_result["original_answer"] = original_response["answer"]
            question_result["original_duration"] = original_response["duration"]
            question_result["original_status"] = original_response["status"]
            
            # Only proceed with verification if we got a valid answer
            if original_response["status"] == "success":
                original_answer = original_response["answer"]
                
                # Process each rephrased question as a verification
                for i in range(1, 4):
                    rephrased_question = row[f'rephrase{i}']
                    logger.debug(f"Processing verification {question_id}, variant {i}")
                    
                    # Check if the question needs to be formatted with the answer
                    if "{answer}" in rephrased_question:
                        verification_response = query_llm_verification(
                            text, original_answer, rephrased_question, args.model, args.timeout
                        )
                    else:
                        # If the rephrased question doesn't have a placeholder, append the answer
                        modified_question = f"{rephrased_question} The answer is: {{{original_answer}}}"
                        verification_response = query_llm_verification(
                            text, original_answer, modified_question, args.model, args.timeout
                        )
                    
                    question_result[f"verification{i}_question"] = rephrased_question
                    question_result[f"verification{i}_result"] = verification_response["verification"]
                    question_result[f"verification{i}_duration"] = verification_response["duration"]
                    question_result[f"verification{i}_status"] = verification_response["status"]
            else:
                # If original question failed, skip verification
                for i in range(1, 4):
                    question_result[f"verification{i}_question"] = row[f'rephrase{i}']
                    question_result[f"verification{i}_result"] = "Skipped - Original question failed"
                    question_result[f"verification{i}_duration"] = 0
                    question_result[f"verification{i}_status"] = "skipped"
            
            results.append(question_result)
            
        return results
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        # Return a partial result indicating the error
        return [{
            "case_name": case_name,
            "error": str(e),
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }]

def init_csv_file(output_path: str, fieldnames: List[str]):
    """
    Initialize a CSV file with header.
    
    Args:
        output_path: Path where the CSV file will be saved
        fieldnames: List of column names for the CSV header
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    
    logger.info(f"Initialized CSV file at {output_path}")

def append_results_to_csv(results: List[Dict[str, Any]], output_path: str, fieldnames: List[str]):
    """
    Append results to a CSV file.
    
    Args:
        results: List of dictionaries containing results
        output_path: Path where the CSV file will be saved
        fieldnames: List of column names for the CSV
    """
    logger.info(f"Appending {len(results)} results to {output_path}")
    
    try:
        # Filter out entries with errors if they don't have the required fields
        valid_results = [r for r in results if "original_question" in r]
        
        if not valid_results:
            logger.warning("No valid results to append to CSV")
            return
        
        with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            for result in valid_results:
                # Extract only the fields we want in the CSV
                row = {
                    "case_name": result["case_name"],
                    "question_id": result["question_id"],
                    "original_question": result["original_question"],
                    "original_answer": result.get("original_answer", ""),
                    "verification1_question": result.get("verification1_question", ""),
                    "verification1_result": result.get("verification1_result", ""),
                    "verification2_question": result.get("verification2_question", ""),
                    "verification2_result": result.get("verification2_result", ""),
                    "verification3_question": result.get("verification3_question", ""),
                    "verification3_result": result.get("verification3_result", "")
                }
                writer.writerow(row)
                
        logger.info(f"Successfully appended {len(valid_results)} results to CSV")
    except Exception as e:
        logger.error(f"Error appending results to CSV: {str(e)}")
        raise

def append_results_to_json(results: List[Dict[str, Any]], output_path: str, case_name: str = None):
    """
    Append results to a JSON file or create a new JSON file for each case.
    
    Args:
        results: List of dictionaries containing results
        output_path: Path where the JSON file will be saved
        case_name: Name of the case (used to create individual JSON files)
    """
    if not output_path:
        return
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # If case_name is provided, save to a separate file
        if case_name:
            # Strip any characters that might cause issues in filenames
            safe_case_name = re.sub(r'[^\w\-_.]', '_', case_name)
            case_output_path = f"{os.path.splitext(output_path)[0]}_{safe_case_name}.json"
            
            logger.info(f"Writing results for case {case_name} to {case_output_path}")
            
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "case_name": case_name,
                "results": results
            }
            
            with open(case_output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            logger.info(f"Successfully wrote results for case {case_name} to JSON")
        else:
            # Append to main JSON file
            # Check if file exists
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        # File exists but is not valid JSON (maybe empty)
                        data = {"timestamp": datetime.now().isoformat(), "results": []}
                
                # Append new results
                data["results"].extend(results)
                data["last_updated"] = datetime.now().isoformat()
            else:
                # Create new file
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }
            
            # Write back to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Successfully updated main JSON file with {len(results)} results")
    except Exception as e:
        logger.error(f"Error updating JSON file: {str(e)}")
        raise

def main():
    """Main function to run the script."""
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set")
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it using:")
        print("  export OPENAI_API_KEY=your_api_key  # On Linux/Mac")
        print("  set OPENAI_API_KEY=your_api_key     # On Windows cmd")
        print("  $env:OPENAI_API_KEY=your_api_key    # On Windows PowerShell")
        return
    
    # Parse arguments
    args = parse_arguments()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Starting Q/A verification for court judgments")
    
    # Read questions CSV
    questions_df = read_questions_csv(args.input_csv)
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(args.pdf_dir) if f.lower().endswith('.pdf')]
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Define CSV columns for the output format
    csv_fieldnames = [
        "case_name", 
        "question_id", 
        "original_question",
        "original_answer",
        "verification1_question", 
        "verification1_result",
        "verification2_question", 
        "verification2_result",
        "verification3_question", 
        "verification3_result"
    ]
    
    # Initialize CSV file with headers
    init_csv_file(args.output_csv, csv_fieldnames)
    
    # Initialize main JSON file if requested
    if args.output_json:
        # Create an empty structure that we'll append to
        init_data = {
            "timestamp": datetime.now().isoformat(),
            "results": []
        }
        
        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(init_data, f, indent=2)
    
    # Process each PDF file and save results incrementally
    for pdf_file in tqdm(pdf_files, desc="Processing PDF files"):
        try:
            pdf_path = os.path.join(args.pdf_dir, pdf_file)
            case_name = extract_case_name(os.path.basename(pdf_file))
            
            # Process the PDF
            results = process_pdf(pdf_path, questions_df, args)
            
            # Append to CSV file
            append_results_to_csv(results, args.output_csv, csv_fieldnames)
            
            # Save to JSON (both individual file and append to main file)
            if args.output_json:
                # Save to individual case file
                append_results_to_json(results, args.output_json, case_name)
                
                # Also append to the main JSON file
                append_results_to_json(results, args.output_json)
                
            logger.info(f"Successfully processed and saved results for {case_name}")
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_file}: {str(e)}")
            # Continue with next PDF
            continue
    
    logger.info("Q/A verification completed successfully")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unhandled exception: {str(e)}")
        raise
