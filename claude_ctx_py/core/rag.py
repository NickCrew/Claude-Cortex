"""RAG (Retrieval Augmented Generation) core functions."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore


class ContextualIngester:
    """Ingests documents with contextual embeddings pattern."""

    def __init__(self, api_key: Optional[str] = None):
        if not anthropic:
            raise ImportError(
                "The 'anthropic' library is required for RAG ingestion. "
                "Install it with: pip install 'claude-cortex[llm]'"
            )
        
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-haiku-20240307"  # Use Haiku for speed/cost

    def chunk_markdown(self, content: str) -> List[Dict[str, str]]:
        """Split markdown content by headers."""
        chunks = []
        # Simple regex to split by headers
        # Matches # Header, ## Header, etc.
        # This is a naive implementation for demonstration
        parts = re.split(r'(^#+\s.*$)', content, flags=re.MULTILINE)
        
        current_chunk = ""
        current_header = "Intro"
        
        for part in parts:
            if re.match(r'^#+\s', part):
                if current_chunk.strip():
                    chunks.append({"header": current_header, "content": current_chunk.strip()})
                current_header = part.strip()
                current_chunk = ""
            else:
                current_chunk += part
        
        if current_chunk.strip():
            chunks.append({"header": current_header, "content": current_chunk.strip()})
            
        return chunks

    def situate_chunk(self, doc_content: str, chunk_content: str) -> str:
        """Generate situating context for a chunk using Claude."""
        
        document_context_prompt = f"""
<document>
{doc_content}
</document>
"""
        chunk_context_prompt = f"""
Here is the chunk we want to situate within the whole document
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only with the succinct context and nothing else.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": document_context_prompt,
                                "cache_control": {"type": "ephemeral"} # Attempt prompt caching
                            },
                            {
                                "type": "text",
                                "text": chunk_context_prompt
                            }
                        ]
                    }
                ],
                extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating context: {e}"

    def ingest_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Ingest a single file."""
        content = file_path.read_text(encoding="utf-8")
        chunks = self.chunk_markdown(content)
        
        ingested_chunks = []
        print(f"Processing {file_path.name} ({len(chunks)} chunks)...")
        
        for i, chunk in enumerate(chunks):
            print(f"  - Situating chunk {i+1}/{len(chunks)}: {chunk['header']}...")
            context = self.situate_chunk(content, chunk['content'])
            
            ingested_chunks.append({
                "file": str(file_path),
                "header": chunk['header'],
                "original_content": chunk['content'],
                "context": context,
                "contextualized_content": f"{context}\n\n{chunk['content']}"
            })
            
        return ingested_chunks
