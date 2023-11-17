#!/usr/bin/env python
# coding: utf-8
"""
Extract text (blog-content) from html, clean it, and save the results.
Organized by metadata.
"""
import argparse
from pathlib import Path
from lxml import html


def collect_attribs(text):
    if text.is_text:
        element = text.getparent()
    elif text.is_tail:
        element = text.getparent().getparent()

    attribs = []
    while element.get('class') != 'paragraph':
        if element.tag != 'br':
            attribs.insert(0, (element.tag, dict(element.attrib)))
        element = element.getparent()

    # paragraph div -> p
    attrib = dict(element.attrib)
    del attrib['class']
    attribs.insert(0, ('p', attrib))

    return attribs


def create_by_attribs(attribs):
    branch = []
    for a in attribs:
        e = html.Element(a[0], attrib=a[1])
        if branch:
            branch[-1].append(e)
        branch.append(e)
    return branch


def first_diff_at(a, b):
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return min_len
    return None


def append_text_to(element, text):
    children = element.getchildren()
    if children:
        children[-1].tail = (children[-1].tail or '') + text
    else:
        element.text = (element.text or '') + text
    return


def extract_text(tree):
    blog = tree.find(".//div[@class='blog-content']")
    paragraphs = blog.findall(".//div[@class='paragraph']")

    ps = []
    for paragraph in paragraphs:
        cur_branch, cur_attribs = None, None
        consec_br = 0

        for t in paragraph.xpath('.//text() | .//br'):
            # <br/>
            if not isinstance(t, str):
                consec_br += 1
                continue

            # text
            if consec_br == 1 and cur_branch:
                cur_branch[-1].append(html.Element('br'))
            elif consec_br > 1 and cur_branch:
                ps.append(cur_branch[0])
                cur_branch, cur_attribs = None, None
            consec_br = 0

            attribs = collect_attribs(t)

            # new branch
            if not cur_branch:
                cur_branch, cur_attribs = create_by_attribs(attribs), attribs
                append_text_to(cur_branch[-1], t)
                continue

            branch_at = first_diff_at(attribs, cur_attribs)

            # same branch
            if branch_at is None:
                append_text_to(cur_branch[-1], t)
                continue

            # restart branch
            if branch_at == 0:
                ps.append(cur_branch[0])
                cur_branch, cur_attribs = create_by_attribs(attribs), attribs
                append_text_to(cur_branch[-1], t)
                continue

            # split branch
            if branch_at < len(cur_attribs):
                cur_branch = cur_branch[:branch_at]
                cur_attribs = cur_attribs[:branch_at]
            if branch_at < len(attribs):
                new_split = create_by_attribs(attribs[branch_at:])
                cur_branch[-1].append(new_split[0])
                cur_branch.extend(new_split)
                cur_attribs.extend(attribs[branch_at:])
            append_text_to(cur_branch[-1], t)

        if cur_branch is not None:
            ps.append(cur_branch[0])

    return ps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pattern', type=str, help='HTML files to process')
    parser.add_argument('out_dir', type=Path, help='Directory to save outputs')
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for file in Path('.').glob(args.pattern):
        print('Processing', file)
        tree = html.parse(file)
        with open(args.out_dir / file.name, 'w', encoding='utf-8') as f:
            for p in extract_text(tree):
                f.write(html.tostring(p, encoding='unicode'))
                f.write('\n')


if __name__ == '__main__':
    main()
