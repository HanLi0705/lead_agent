import arxiv
import argparse
import sys

def search_arxiv(query, max_results=5):
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in search.results():
            results.append(f"Title: {result.title}")
            results.append(f"Authors: {', '.join(author.name for author in result.authors)}")
            results.append(f"Published: {result.published}")
            results.append(f"URL: {result.entry_id}")
            results.append(f"Summary: {result.summary}")
            results.append("-" * 40)
        
        if not results:
            return "No papers found for the given query."
        return "\n".join(results)
    except Exception as e:
        return f"Error searching arXiv: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search arXiv for papers")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max_results", type=int, default=5, help="Maximum number of results")
    
    args = parser.parse_args()
    print(search_arxiv(args.query, args.max_results))
