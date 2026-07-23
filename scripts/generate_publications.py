from pathlib import Path
import bibtexparser
import re

# ------------------------------------------------------------------
# USER SETTINGS
# ------------------------------------------------------------------

MY_FIRST = "Jonathan"
MY_LAST = "Kho"

INPUT = Path("assets/papers.bib")
OUTPUT = Path("publications.qmd")

# ------------------------------------------------------------------

def format_authors(author_string):
    """
    Formats ADS BibTeX author lists.

    Converts

        {Kho}, Jonathan

    into

        **Jonathan Kho**

    while removing all braces.
    """

    formatted = []

    authors = author_string.split(" and ")

    for author in authors:

        # Remove ADS braces
        author = author.replace("{", "").replace("}", "").strip()

        if "," in author:

            last, first = [x.strip() for x in author.split(",", 1)]

            display = f"{first} {last}"

        else:

            display = author

            parts = display.split()

            if len(parts) >= 2:
                first = parts[0]
                last = parts[-1]
            else:
                first = display
                last = ""

        if (
            first.lower() == MY_FIRST.lower()
            and last.lower() == MY_LAST.lower()
        ):
            display = f"**{display}**"

        formatted.append(display)

    return ", ".join(formatted)

def first_author(entry):

    authors = entry.get("author", "").split(" and ")

    if len(authors) == 0:
        return False

    first = authors[0].lower()

    return (
        MY_LAST.lower() in first
        and MY_FIRST.lower() in first
    )


with open(INPUT, encoding="utf8") as bibfile:
    library = bibtexparser.load(bibfile)

first = []
coauthor = []

for entry in library.entries:

    if first_author(entry):
        first.append(entry)
    else:
        coauthor.append(entry)


def sort_entries(entries):

    return sorted(
        entries,
        key=lambda e: int(e.get("year", 0)),
        reverse=True,
    )


first = sort_entries(first)
coauthor = sort_entries(coauthor)


def write_section(outfile, title, entries):

    outfile.write(f"# {title}\n\n")

    for e in entries:

        title = e.get("title", "").strip("{}")

        authors = format_authors(e.get("author", ""))

        journal = (
            e.get("journal")
            or e.get("booktitle")
            or ""
        )

        year = e.get("year", "")

        outfile.write(f"## {title}\n\n")

        outfile.write(authors + "\n\n")

        if journal:

            outfile.write(f"*{journal}*")

            if year:
                outfile.write(f", {year}")

            outfile.write("\n\n")

        links = []

        doi = e.get("doi", "")

        url = e.get("url", "")

        adsurl = e.get("adsurl", "")

        eprint = e.get("eprint", "")

        if doi:
            links.append(
                f"[DOI](https://doi.org/{doi})"
            )

        if adsurl:
            links.append(
                f"[ADS]({adsurl})"
            )

        if eprint:
            links.append(
                f"[arXiv](https://arxiv.org/abs/{eprint})"
            )

        elif (
            url
            and "arxiv.org" in url
        ):
            links.append(
                f"[arXiv]({url})"
            )

        elif url:
            links.append(
                f"[Journal]({url})"
            )

        if links:

            outfile.write(
                " | ".join(links)
            )

            outfile.write("\n\n")

        outfile.write("---\n\n")


with open(OUTPUT, "w", encoding="utf8") as out:

    out.write("---\n")
    out.write('title: "Publications"\n')
    out.write("---\n\n")

    write_section(
        out,
        "First-author Publications",
        first,
    )

    write_section(
        out,
        "Co-authored Publications",
        coauthor,
    )

print("Generated publications.qmd")
