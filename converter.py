import re
import argparse


def parseLine(line):
    res = re.sub(r"\*\*(.*)\*\*", r"\\textbf{\1}", line)
    res = re.sub(r"\*(.*)\*", r"\\textit{\1}", res)
    res = re.sub(r"\_\_(.*)\_\_", r"\\underline{\1}", res)
    res = re.sub(r"\~\~(.*)\~\~", r"\\sout{\1}", res)
    res = re.sub(r"\[(.*)\] *\((.*)\)", r"\\href{\2}{\1}", res)
    return res


def convert(file, output, author, ct, nonums):
    sec = "section"
    if nonums:
        sec = "section*"
    pdf = ""
    pdf += "\\documentclass[a4paper,12pt]{article}\n"

    # packages
    pdf += "\\usepackage[normalem]{ulem}\n"
    pdf += "\\usepackage{hyperref}\n"
    pdf += "\\hypersetup{colorlinks=true, linkcolor=blue, filecolor=magenta, urlcolor=cyan, pdfpagemode=FullScreen}\n"
    pdf += "\\urlstyle{same}\n"

    if author != "":
        pdf += "\\author{"+author+"}\n"
    pdf += "\\begin{document}\n"
    title = ""
    aftertext = ""
    with open(file, "r") as f:
        currentListDepth = -1
        line = f.readline()
        while line != "":
            if not re.match(r"^ *[*-+] .*$", line) and currentListDepth != -1:
                while currentListDepth != -1:
                    aftertext += "\\end{itemize}\n"
                    currentListDepth -= 1

            if re.match(r"^# .*$", line):
                title = line[2:-1]
            elif re.match(r"^## .*$", line):
                aftertext += "\\" + sec + "{" + line[3:-1] + "}\n"
            elif re.match(r"^### .*$", line):
                aftertext += "\sub" + sec + "{" + line[4:-1] + "}\n"
            elif re.match(r"^#### .*$", line):
                aftertext += "\subsub" + sec + "{" + line[5:-1] + "}\n"
            elif re.match(r"^ *[*-+] .*$", line):
                spaces = len(line) - len(line.lstrip(' '))
                if spaces/2 > currentListDepth:
                    aftertext += "\\begin{itemize}\n"
                    currentListDepth += 1
                elif spaces/2 < currentListDepth:
                    aftertext += "\\end{itemize}\n"
                    currentListDepth -= 1

                aftertext += "\\item " + line[spaces+2:]

            else:
                aftertext += parseLine(line) + " \\\\ \n"

            line = f.readline()

    # writeback
    pdf += "\\title{"+title+"}\n\\maketitle\n"
    if ct:
        pdf += "\\tableofcontents"
    pdf += "\\newpage\n"
    pdf += aftertext
    pdf += "\\end{document}"
    with open(output, "w") as f:
        f.write(pdf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--contenttable",
                        action="store_true", help="Enable a content table")
    parser.add_argument("-a", "--author", type=str, default="")
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, default="output.tex")
    parser.add_argument("--nonums", action="store_true")
    args = parser.parse_args()
    convert(args.input, args.output, args.author,
            args.contenttable, args.nonums)
