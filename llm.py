# -*- coding: utf-8 -*-
"""LLM.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kzDD0gG-F9lcFUTOEjlSBLubCGd9BRUR
"""

!pip install faker

from faker import Faker
import random

fake = Faker()
from datetime import date
from dateutil.relativedelta import relativedelta

six_months = date.today() - relativedelta(months=+6)
three_months = date.today() - relativedelta(months=+3)
months = [three_months, six_months]

# Generate demographic and personal information
def generate_customer_data():
    age = random.randint(20, 70)
    gender = random.choice(['Male', 'Female'])
    marital_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
    income_level = random.choice(['Low', 'Medium', 'High'])
    education = random.choice(['High School', 'College', 'University'])
    occupation = fake.job()
    residential_status = random.choice(['Owns house', 'Rents', 'Living with parents'])
    dependents = random.randint(0, 5),  # Number of dependents
    debt_to_income = round(random.uniform(0.1, 0.5), 2),  # Debt-to-income ratio
    credit_bureau = random.randint(760, 850)

    return {
        'Age': age,
        'Gender': gender,
        'Marital Status': marital_status,
        'Income Level': income_level,
        'Education': education,
        'Occupation': occupation,
        'Residential Status': residential_status,
        'Dependents': dependents,
        'Debt-to-Income': debt_to_income,
        'Credit_Bureau': credit_bureau
    }

# Function to generate bureau product inquiries
def generate_inquiries(last_months):
    inquiries = []
    today = fake.date_this_month()

    # Generate inquiries for the last `last_months` period
    for _ in range(random.randint(1, 5)):  # Random number of inquiries
        inquiry_date = fake.date_between(start_date=last_months, end_date=today)
        product_type = random.choice(['Personal Loan', 'Credit Card', 'Mortgage'])
        inquiries.append({'product_name': product_type, 'date': inquiry_date})

    return inquiries if inquiries else []

# Function to generate dataset
def generate_dataset(num_rows,months):
    data_rows = []

    for _ in range(num_rows):
        customer_data = generate_customer_data()
        last_3_months_inquiries = generate_inquiries(months[0])
        last_6_months_inquiries = generate_inquiries(months[1])

        # Initialize columns for each product type
        customer_row = {
            'Customer ID': fake.uuid4(),
            'Age': customer_data['Age'],
            'Gender': customer_data['Gender'],
            'Marital Status': customer_data['Marital Status'],
            'Income Level': customer_data['Income Level'],
            'Education': customer_data['Education'],
            'Occupation': customer_data['Occupation'],
            'Residential Status': customer_data['Residential Status'],
            'Dependents': customer_data['Dependents'],
            'Debt-to-Income': customer_data['Debt-to-Income'],
            'Credit_Bureau': customer_data['Credit_Bureau']
        }

        # Process last 3 months inquiries
        for product_type in ['Personal Loan', 'Credit Card', 'Mortgage']:
            inq_in_last_3_months = any(inq['product_name'] == product_type for inq in last_3_months_inquiries)
            customer_row[f'last_3months_{product_type.replace(" ", "_").lower()}_inq'] = inq_in_last_3_months

        # Process last 6 months inquiries
        for product_type in ['Personal Loan', 'Credit Card', 'Mortgage']:
            inq_in_last_6_months = any(inq['product_name'] == product_type for inq in last_6_months_inquiries)
            customer_row[f'last_6months_{product_type.replace(" ", "_").lower()}_inq'] = inq_in_last_6_months

        data_rows.append(customer_row)

    return data_rows

# Example usage to generate 50 rows of data
dataset = generate_dataset(50, months)

# Example usage to generate 50 rows of data
dataset = generate_dataset(50, months)

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')
df = pd.DataFrame(dataset)
df.to_csv("products_info.csv")

df.head()

dataset[0]

df['content'] = [f"Based on the following customer data: {data}, suggest suitable banking lending products." for data in dataset]
df.head()

df['content'][0]

!pip install langchain langchain-community langchain-core transformers

from langchain.docstore.document import Document

# Prepare documents for LangChain
documents = []
for _, row in df.iterrows():
    documents.append(Document(page_content=row["content"], metadata={"class": row["Age"]}))

!pip install sentence-transformers

!pip install chromadb
!pip install bitsandbytes accelerate

from langchain_community.embeddings import HuggingFaceEmbeddings
hg_embeddings = HuggingFaceEmbeddings()

from langchain.vectorstores import Chroma

persist_directory = '/content/'

langchain_chroma = Chroma.from_documents(
    documents=documents,
    collection_name="recommendation_engine",
    embedding=hg_embeddings,
    persist_directory=persist_directory
)

from torch import cuda, bfloat16
import torch
import transformers
from transformers import AutoTokenizer
from time import time
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma

model_id = 'HuggingFaceH4/zephyr-7b-beta'

device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

# set quantization configuration to load large model with less GPU memory
# this requires the `bitsandbytes` library
bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=bfloat16
)

print(device)

import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

model_config = transformers.AutoConfig.from_pretrained(
   model_id,
    trust_remote_code=True,
    max_new_tokens=1024
)
model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    config=model_config,
    quantization_config=bnb_config,
    device_map='auto',
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Initialize the query pipeline with increased max_length
query_pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.float16,
    max_length=6000,  # Increase max_length
    max_new_tokens=500,  # Control the number of new tokens generated
    device_map="auto",
)

from IPython.display import display, Markdown
def colorize_text(text):
    for word, color in zip(["Reasoning", "Question", "Answer", "Total time"], ["blue", "red", "green", "magenta"]):
        text = text.replace(f"{word}:", f"\n\n**<font color='{color}'>{word}:</font>**")
    return text

llm = HuggingFacePipeline(pipeline=query_pipeline)

question = "What is Recommendation Engie and How it used in Finance Domain?"
response = llm(prompt=question)

full_response =  f"Question: {question}\nAnswer: {response}"
display(Markdown(colorize_text(full_response)))