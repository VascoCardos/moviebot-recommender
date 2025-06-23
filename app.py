from flask import Flask, render_template, request, jsonify
import csv
import os
import openai # Importa a biblioteca OpenAI
from dotenv import load_dotenv # Para carregar variáveis de ambiente do .env
from typing import List, Dict, Optional
import json
from groq import Groq

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

class MovieDatabase:
  def __init__(self, csv_path: str = "movies.csv"):
      self.movies = []
      self.load_movies(csv_path)
  
  def load_movies(self, csv_path: str):
      """Load movies from CSV file"""
      sample_movies = [ # Fallback
          {"movieId": "1", "title": "Inception (2010)", "genres": "Action|Drama|Sci-Fi|Thriller", "year": "2010", "rating": "8.8"},
          {"movieId": "2", "title": "The Dark Knight (2008)", "genres": "Action|Crime|Drama|IMAX", "year": "2008", "rating": "9.0"},
      ]
      
      if os.path.exists(csv_path):
          try:
              with open(csv_path, 'r', encoding='utf-8') as file:
                  reader = csv.DictReader(file)
                  self.movies = list(reader)
          except Exception as e:
              print(f"Error loading CSV: {e}. Using sample movies.")
              self.movies = sample_movies
      else:
          print(f"CSV file not found at {csv_path}. Using sample movies.")
          self.movies = sample_movies
  
  def get_movies_context(self, limit: int = 100) -> str:
      """Get formatted movie context for LLM"""
      if not self.movies:
          return "No movies available in the database.\n"
          
      movies_text = "Available Movies Database (Title (Year) | Genres | Rating/10):\n"
      for movie in self.movies[:limit]:
          title = movie.get('title', 'N/A')
          year = movie.get('year', 'N/A')
          genres = movie.get('genres', 'N/A')
          rating = movie.get('rating', 'N/A')
          movies_text += f"- {title} ({year}) | Genres: {genres} | Rating: {rating}/10\n"
      return movies_text

class LLMService:
  def __init__(self):
      self.llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
      self.openai_api_key = os.getenv('OPENAI_API_KEY')
      self.groq_api_key = os.getenv('GROQ_API_KEY')
      # Add other API key retrievals here if needed (e.g., TogetherAI)

      self.client = None

      if self.llm_provider == 'openai':
          if self.openai_api_key:
              openai.api_key = self.openai_api_key
              print("OpenAI API Key carregada com sucesso.")
          else:
              print("AVISO: OPENAI_API_KEY não encontrada para o provedor OpenAI. O MovieBot usará respostas simuladas.")
      elif self.llm_provider == 'groq':
          if self.groq_api_key:
              self.client = Groq(api_key=self.groq_api_key)
              print("Groq API Key carregada com sucesso.")
          else:
              print("AVISO: GROQ_API_KEY não encontrada para o provedor Groq. O MovieBot usará respostas simuladas.")
      # Add elif blocks for other providers like 'togetherai'
      else:
          print(f"AVISO: Provedor LLM '{self.llm_provider}' não suportado ou API key não encontrada. Usando respostas simuladas.")

      if not self.is_api_configured():
          print("Nenhuma API LLM configurada corretamente. MovieBot usará respostas simuladas.")

  def is_api_configured(self) -> bool:
      """Check if the selected LLM provider is configured with an API key."""
      if self.llm_provider == 'openai' and self.openai_api_key:
          return True
      if self.llm_provider == 'groq' and self.client: # self.client is the Groq client
          return True
      # Add checks for other providers
      return False

  def get_system_prompt(self, user_type: str) -> str:
      """Generate system prompt based on user type"""
      base_prompt = """You are MovieBot, an intelligent movie recommendation assistant. You have access to a curated movie database (provided below the user query) and should provide personalized recommendations based on user queries.

Your responses MUST:
1. Be conversational and engaging.
2. Provide 3-5 specific movie recommendations STRICTLY from the provided "Available Movies Database" context.
3. For each recommendation, include its Title, Year, and Rating as listed in the database.
4. Include brief explanations for why each movie fits the request, linking it to the user's query.
5. Consider the user's preferences and viewing style (casual, critic, enthusiast).
6. Format recommendations clearly. Example: 🎬 **Movie Title (Year)** - Rating: X.X/10. Explanation...
7. If the query is too vague or the movies in the database don't fit well, you can ask for clarification or suggest broader categories based on the available movies.
8. DO NOT invent movies or details not present in the "Available Movies Database". If a movie from the query is not in the database, state that and try to find similar ones that ARE in the database.
9. If no suitable movies are found in the database for the query, clearly state that and perhaps suggest how the user could rephrase their query.
"""

      user_prompts = {
          "casual": "The user is a casual movie watcher who enjoys popular, accessible films. Focus on mainstream hits and crowd-pleasers. Keep explanations concise and fun.",
          "critic": "The user is a film critic who appreciates artistic merit, cinematography, and storytelling craft. Recommend critically acclaimed and technically excellent films. Provide more detailed and analytical explanations.",
          "enthusiast": "The user is a genre enthusiast who loves exploring specific movie categories deeply. Provide detailed genre-specific recommendations with nuanced explanations, possibly mentioning sub-genres or specific cinematic techniques if relevant."
      }
      return base_prompt + user_prompts.get(user_type, user_prompts["casual"])

  def get_recommendations(self, query: str, user_type: str, movies_context: str) -> str:
      """Get movie recommendations from LLM"""
      if not self.is_api_configured():
          print("Usando resposta simulada devido à falta de configuração de API Key.")
          return self.simulate_llm_response(query, user_type, movies_context)

      system_prompt_content = self.get_system_prompt(user_type)
      user_query_with_context = f"User Query: {query}\n\nUser Type: {user_type}\n\n{movies_context}\n\nBased on the query, user type, and ONLY the movies listed in the 'Available Movies Database' above, provide recommendations."
      
      messages = [
          {"role": "system", "content": system_prompt_content},
          {"role": "user", "content": user_query_with_context}
      ]

      try:
          if self.llm_provider == 'openai':
              print(f"Enviando para OpenAI API. System prompt (início): {system_prompt_content[:150]}...")
              print(f"User message with context (início): {user_query_with_context[:200]}...")
              completion = openai.chat.completions.create( # Assumes openai library version < 1.0 or appropriately configured
                  model="gpt-3.5-turbo", 
                  messages=messages,
                  temperature=0.7,
                  max_tokens=600 
              )
              response_text = completion.choices[0].message.content
              print(f"Resposta da OpenAI (início): {response_text[:150]}...")
              return response_text.strip()
          
          elif self.llm_provider == 'groq' and self.client:
              print(f"Enviando para Groq API. System prompt (início): {system_prompt_content[:150]}...")
              print(f"User message with context (início): {user_query_with_context[:200]}...")
              completion = self.client.chat.completions.create(
                  model="llama3-8b-8192", # Or another model available on Groq like "mixtral-8x7b-32768"
                  messages=messages,
                  temperature=0.7,
                  max_tokens=600
              )
              response_text = completion.choices[0].message.content
              print(f"Resposta da Groq (início): {response_text[:150]}...")
              return response_text.strip()
          
          # Add elif blocks for other providers
          else: # Fallback if provider logic is missing but somehow passed is_api_configured
              print(f"Provedor {self.llm_provider} não implementado corretamente.")
              return self.simulate_llm_response(query, user_type, movies_context)

      except Exception as e:
          print(f"Erro ao chamar a API da {self.llm_provider.upper()}: {e}")
          print("Retornando resposta simulada devido ao erro.")
          return self.simulate_llm_response(query, user_type, movies_context)

  def simulate_llm_response(self, query: str, user_type: str, movies_context: str) -> str:
      """Simulate LLM response for demo purposes or fallback"""
      # (Mantendo a função de simulação como estava antes para fallback)
      query_lower = query.lower()
      if "inception" in query_lower:
          return """🎬 **Filmes simulados para 'Inception':**

🎭 **The Matrix (1999)** - Rating: 8.7/10 (Simulado)
Realidade vs. simulação com ação espetacular.

🎭 **Memento (2000)** - Rating: 8.4/10 (Simulado) 
Narrativa não-linear sobre memória."""
      return "Resposta simulada: Não foi possível conectar à API ou chave não configurada. Verifique o console para mais detalhes."

# Initialize services
movie_db = MovieDatabase()
llm_service = LLMService()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
  try:
      data = request.get_json()
      query = data.get('query', '')
      user_type = data.get('user_type', 'casual')
      
      if not query:
          return jsonify({'error': 'Query is required'}), 400
      
      movies_context = movie_db.get_movies_context()
      if "No movies available" in movies_context:
           print("AVISO: A base de dados de filmes parece estar vazia ou não foi carregada.")
      
      recommendations = llm_service.get_recommendations(query, user_type, movies_context)
      
      return jsonify({
          'recommendations': recommendations,
          'query': query,
          'user_type': user_type
      })
  
  except Exception as e:
      print(f"Erro na rota /recommend: {e}")
      return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  # Certifique-se que o python-dotenv foi importado e load_dotenv() chamado no topo.
  app.run(debug=True)
