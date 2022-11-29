#!/usr/bin/env python
"""
performs_data_cleaning_and_save_result_to_wandb
"""
import os
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################

    logger.info("Downloading artifact from W&B for basic data cleaning")
    
    # collect artifact from W&B
    artifact = run.use_artifact(args.input_artifact)

    # get path to downloaded artifact
    artifact_path = artifact.file()

    # read artifact into pandas
    df = pd.read_csv(artifact_path)

    #### BASIC CLEANING #########
    # Drop price outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # mahe sure coordinates are within these boundaries
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Assign name for cleaned dataset and save locally without the index
    filename = args.output_artifact
    df.to_csv(filename, index=False)

    # Create new artifact in W&B
    artifact = wandb.Artifact(
                                args.output_artifact,
                                type=args.output_type,
                                description=args.output_description,
                                )

    # Attach cleaned dataset to new artifact                            
    artifact.add_file("clean_sample.csv")
    # upload to W&B
    run.log_artifact(artifact)
    
    # remove local temporary file
    os.remove(filename)

    logger.info("Finished basic cleaning - Cleaned dataset uploaded to wandb")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="this_step_cleans_the_data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualified name for the input artifact, ie the raw dataset",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the output cleaned artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type for the artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="miminum price to consider for the analysis",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="maximum price to consider for the analysis",
        required=True
    )


    args = parser.parse_args()

    go(args)
