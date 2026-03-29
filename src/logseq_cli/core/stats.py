from __future__ import annotations

from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Graph
from logseq_cli.core.tasks import list_tasks


def graph_stats(graph: Graph) -> dict[str, int]:
    page_paths = list(iter_documents(graph.pages_dir))
    journal_paths = list(iter_documents(graph.journals_dir))
    all_paths = [*page_paths, *journal_paths]

    markdown_documents = sum(1 for path in all_paths if path.suffix.lower() == ".md")
    org_documents = sum(1 for path in all_paths if path.suffix.lower() == ".org")
    tasks = list_tasks(graph)

    return {
        "pages": len(page_paths),
        "journals": len(journal_paths),
        "documents": len(all_paths),
        "markdown_documents": markdown_documents,
        "org_documents": org_documents,
        "tasks": len(tasks),
    }
