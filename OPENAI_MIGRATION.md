# OpenAI Migration Guide

This document outlines the changes made to migrate from Google Gemini to OpenAI in the DataWise project.

## 🔄 **Changes Made**

### **1. Dependencies Updated**

#### **Backend/requirements.txt**
```diff
- genkit==1.14.1
- @genkit-ai/googleai==1.14.1
+ openai==1.12.0
```

### **2. Environment Variables**

#### **Backend/env.example**
```diff
- GOOGLE_AI_API_KEY=your-google-ai-api-key-here
+ OPENAI_API_KEY=your-openai-api-key-here
```

#### **docker-compose.yml**
```diff
- GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
+ OPENAI_API_KEY=${OPENAI_API_KEY}
```

### **3. Configuration Updates**

#### **Backend/app/core/config.py**
```diff
- GOOGLE_AI_API_KEY: str
+ OPENAI_API_KEY: str
```

### **4. LLM Service Implementation**

#### **Backend/app/services/llm_service.py**

**Before (Google AI with Genkit):**
```python
from genkit import genkit
from genkit.ai.googleai import googleAI

class LLMService:
    def __init__(self, db: Session):
        self.ai = genkit({
            "plugins": [googleAI()],
            "model": "googleai/gemini-2.0-flash",
            "googleAI": {
                "apiKey": settings.GOOGLE_AI_API_KEY
            }
        })
    
    def generate_sql_from_prompt(self, prompt: str, context: Dict[str, Any]):
        response = self.ai.generate(sql_generation_prompt)
        sql_query = response.text.strip()
```

**After (OpenAI):**
```python
from openai import OpenAI

class LLMService:
    def __init__(self, db: Session):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_sql_from_prompt(self, prompt: str, context: Dict[str, Any]):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only SQL queries, no explanations."},
                {"role": "user", "content": sql_generation_prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        sql_query = response.choices[0].message.content.strip()
```

### **5. LLM Query Processing**

**Before:**
```python
response = self.ai.generate(enhanced_prompt)
return LLMQueryResponse(
    response=response.text,
    sql_generated=sql_generated,
    confidence_score=0.85,
    execution_time_ms=execution_time
)
```

**After:**
```python
response = self.client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an AI assistant with access to a database. Answer questions based on the available data."},
        {"role": "user", "content": enhanced_prompt}
    ],
    max_tokens=1000,
    temperature=0.7
)
ai_response = response.choices[0].message.content

return LLMQueryResponse(
    response=ai_response,
    sql_generated=sql_generated,
    confidence_score=0.85,
    execution_time_ms=execution_time
)
```

## 🚀 **Benefits of OpenAI Migration**

### **✅ Advantages**
1. **Better SQL Generation**: GPT-4 is excellent at SQL query generation
2. **More Reliable**: OpenAI's API is very stable and well-documented
3. **Better Context Understanding**: GPT-4 handles complex prompts better
4. **Wider Adoption**: More developers familiar with OpenAI
5. **Better Error Handling**: More detailed error messages

### **🔧 Configuration**
- **Model**: `gpt-4` (can be changed to `gpt-3.5-turbo` for cost savings)
- **Max Tokens**: 500 for SQL generation, 1000 for general responses
- **Temperature**: 0.1 for SQL (deterministic), 0.7 for general responses

## 📋 **Setup Instructions**

### **1. Get OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### **2. Set Environment Variable**
```bash
# For Docker
export OPENAI_API_KEY=sk-your-api-key-here

# For local development
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

### **3. Test the Integration**
```bash
# Start the application
docker-compose up

# Test LLM queries in the frontend
# Visit: http://localhost:9002
# Login and try LLM queries
```

## 🔍 **Testing Examples**

### **SQL Generation**
- Input: "Show me sales by region"
- Expected: `SELECT region, SUM(sales_amount) FROM sales_data GROUP BY region`

### **Natural Language Queries**
- Input: "What are the top selling products?"
- Expected: AI response with analysis and generated SQL

## 💰 **Cost Considerations**

### **OpenAI Pricing (as of 2024)**
- **GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **GPT-3.5-turbo**: $0.0015 per 1K input tokens, $0.002 per 1K output tokens

### **Cost Optimization**
```python
# For cost-sensitive applications, use GPT-3.5-turbo
model="gpt-3.5-turbo"  # Instead of "gpt-4"

# Reduce max_tokens for shorter responses
max_tokens=300  # Instead of 500/1000
```

## 🔄 **Rollback Instructions**

If you need to rollback to Google AI:

1. **Revert requirements.txt:**
   ```bash
   # Remove openai, add back genkit
   pip uninstall openai
   pip install genkit @genkit-ai/googleai
   ```

2. **Revert environment variables:**
   ```bash
   # Change OPENAI_API_KEY back to GOOGLE_AI_API_KEY
   ```

3. **Revert LLM service:**
   ```python
   # Replace OpenAI client with Genkit setup
   ```

## ✅ **Migration Complete**

The migration from Google Gemini to OpenAI is now complete. The application will use GPT-4 for:
- SQL query generation from natural language
- AI-powered database analysis
- Context-aware responses

All existing functionality remains the same, but with improved AI capabilities! 