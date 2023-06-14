# -*- coding: utf-8 -*-
#
# extractor_userdocs.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import re
from typing import List
from tqdm import tqdm
from pathlib import Path
from pprint import pformat
from copy import deepcopy
from math import comb
from textwrap import indent
from itertools import chain
from fnmatch import fnmatch, filter as fnfilter
from dataclasses import dataclass, field

import os
import glob
import json
from itertools import chain, combinations
import logging
from collections import Counter
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class NoUserDocs(ValueError):
    def __init__(self, filename, message=None, *args, **kwargs):
        if not message:
            message = f"No user documentation found in {filename}"
        self._filename = filename
        super().__init__(message, *args, **kwargs)


@dataclass
class DocMeta:
    filename: Path = field(default_factory=Path)
    keywords: List[str] = field(default_factory=list)
    userdoc: str = field(default_factory=str)
    def __post_init__(self):
        if self.filename is not None:
            self._readfile()

    def _readfile(self):
        '''
        Extract the documentation meta sections.
        '''
        userdoc_re = re.compile(r'BeginUserDocs:?\s*(?P<tags>([\w -]+(,\s*)?)*)\n+(?P<doc>(.|\n)*)EndUserDocs')
        match = None
        with self.filename.open('r', encoding='utf8') as infile:
            match = userdoc_re.search(infile.read())
        if not match:
            raise NoUserDocs(self.filename)

        log.info("extracted user documentation from %s...", self.filename)
        self.keywords = list(t.strip() for t in match.group('tags').split(','))            # refactor this to re.split
        self.userdoc = str(match.group('doc'))



class TagIndex:
    def __init__(self):
        self._tagdict = {}

    def update(self, name, tags):
        for tag in tags:
            if not tag.strip():
                log.warning("skipping tag %s for %s", repr(tag), name)
                continue
            self._tagdict.setdefault(tag, list()).append(name)

    @property
    def tags(self):
        yield from self._tagdict.keys()

    @property
    def files(self):
        yield from set.union(*[set(x) for x in tagdict.values()])

    def __getitem__(self, tag):
        return self._tagdict[tag]

    def scan_files(self, filenames):
        log.info("indexing keywords...")
        nfiles, nfiles_total = 0, 0
        for filename in filenames:
            nfiles_total += 1
            try:
                log.debug("scanning %s...", filename)
                meta = DocMeta(filename)
                nfiles += 1
                log.debug("    keywords: %s", meta.keywords)
                self.update(filename, meta.keywords)
            except NoUserDocs as nodoc:
                log.warning(nodoc)
            except UnicodeDecodeError as exc:
                log.warning("probably an incorrect input file: %s:", filename)
                log.warning(exc)

        log.info("found tags:")
        for tag in self.tags:
            log.info(" %5d %s", len(self[tag]), tag)
        log.debug("%4d files in input", nfiles_total)
        log.debug("%4d files with documentation", nfiles)


def UserDocExtractor(
        filenames,
        basedir="..",
        replace_ext='.rst',
        outdir="userdocs/"
        ):
    """
    Extract all user documentation from given files.

    This method searches for "BeginUserDocs" and "EndUserDocs" keywords and
    extracts all text inbetween as user-level documentation. The keyword
    "BeginUserDocs" may optionally be followed by a colon ":" and a comma
    separated list of tags till the end of the line. Note that this allows tags
    to contain spaces, i.e. you do not need to introduce underscores or hyphens
    for multi-word tags.

    Example
    -------

    /* BeginUserDocs: example, user documentation generator

    [...]

    EndUserDocs */

    This will extract "[...]" as documentation for the file and tag it with
    'example' and 'user documentation generator'.

    The extracted documentation is written to a file in `basedir` named after
    the sourcefile with ".rst" replacing the original extension.

    Parameters
    ----------

    filenames : iterable
       Any iterable with input file names (relative to `basedir`).

    basedir : str, path
       Directory to which input `filenames` are relative.

    replace_ext : str
       Replacement for the extension of the original filename when writing to `outdir`.

    outdir : str, path
       Directory where output files are created.

    Returns
    -------

    dict
       mapping tags to lists of documentation filenames (relative to `outdir`).
    """
    raise NotImplementedError("This function was split up.")
    #if not os.path.exists(outdir):
    #    log.info("creating output directory "+outdir)
    #    os.mkdir(outdir)
    #userdoc_re = re.compile(r'BeginUserDocs:?\s*(?P<tags>([\w -]+(,\s*)?)*)\n+(?P<doc>(.|\n)*)EndUserDocs')
    #tagdict = dict()    # map tags to lists of documents
    #nfiles_total = 0
    #with tqdm(unit="files", total=len(filenames)) as progress:
    #    for filename in filenames:
    #        progress.set_postfix(file=os.path.basename(filename)[:15], refresh=False)
    #        progress.update(1)
    #        log.info("extracting user documentation from %s...", filename)
    #        match = None
    #        with open(os.path.join(basedir, filename), 'r', encoding='utf8') as infile:
    #            match = userdoc_re.search(infile.read())
    #        if not match:
    #            log.info("No user documentation found in " + filename)
    #            continue
    #        outname = os.path.basename(os.path.splitext(filename)[0]) + replace_ext
    #        tags = [t.strip() for t in match.group('tags').split(',')]
    #        for tag in tags:
    #            tagdict.setdefault(tag, list()).append(outname)
    #        doc = match.group('doc')
    #        try:
    #            doc = rewrite_short_description(doc, filename)
    #        except ValueError as e:
    #            log.warning("Documentation added unfixed: %s", e)
    #        try:
    #            doc = rewrite_see_also(doc, filename, tags)
    #        except ValueError as e:
    #            log.info("Failed to rebuild 'See also' section: %s", e)
    #        write_rst_files(doc, tags, outdir, outname)

    #log.info("%4d tags found:\n%s", len(tagdict), pformat(list(tagdict.keys())))
    #nfiles = len(set.union(*[set(x) for x in tagdict.values()]))
    #log.info("%4d files in input", nfiles_total)
    #log.info("%4d files with documentation", nfiles)
    #return tagdict


def rewrite_short_description(doc, short_description="Short description"):
    '''
    Modify a given text by replacing the first section named as given in
    `short_description` by the filename and content of that section.

    Parameters
    ----------
    doc : DocMeta
      restructured text with all sections
    short_description : str
      title of the section that is to be rewritten to the document title

    Returns
    -------
    DocMeta
        original parameter doc with short_description section replaced
    '''

    titles = getTitles(doc.userdoc)
    if not titles:
        raise ValueError("No sections found in '%s'!" % doc.filename)
    name = doc.filename.stem
    for title, nexttitle in zip(titles, titles[1:]+[None]):
        if title.group(1) != short_description:
            continue
        secstart = title.end()
        secend = len(doc.userdoc) + 1  # last section ends at end of document
        if nexttitle:
            secend = nexttitle.start()
        sdesc = doc.userdoc[secstart:secend].strip().replace('\n', ' ')
        fixed_title = "%s – %s" % (name, sdesc)
        newdoc = deepcopy(doc)
        newdoc.userdoc = doc.userdoc[:title.start()] + \
            fixed_title + "\n" + "=" * len(fixed_title) + "\n\n" + \
            doc.userdoc[secend:]
        return newdoc
    raise ValueError("No section '%s' found in %s!" % (short_description, doc.filename))


def rewrite_see_also(doc, see_also="See also"):
    '''
    Replace the content of a section named `see_also` in the document `doc`
    with links to indices of all its tags.
    The original content of the section -if not empty- will discarded and
    logged as a warning.

    Parameters
    ----------
    doc : DocMeta
      restructured text with all sections
    see_also : str
      title of the section that is to be rewritten to the document title

    Returns
    -------
    DocMeta
        original parameter doc with see_also section replaced
    '''

    titles = getTitles(doc.userdoc)
    if not titles:
        raise ValueError("No sections found in '%s'!" % doc.filename)

    def rightcase(text):
        '''
        Make text title-case except for acronyms, where an acronym is
        identified simply by being all upper-case.
        This function operates on the whole string, so a text with mixed
        acronyms and non-acronyms will not be recognized and everything will be
        title-cased, including the embedded acronyms.
        Parameters
        ----------
        text : str
          text that needs to be changed to the right casing.
        Returns
        -------
        str
          original text with poentially different characters being
          upper-/lower-case.
        '''
        if text != text.upper():
            return text.title()  # title-case any tag that is not an acronym
        return text   # return acronyms unmodified

    for title, nexttitle in zip(titles, titles[1:]+[None]):
        if title.group(1) != see_also:
            continue
        secstart = title.end()
        secend = len(doc.userdoc) + 1  # last section ends at end of document
        if nexttitle:
            secend = nexttitle.start()
        original = doc.userdoc[secstart:secend].strip().replace('\n', ' ')
        if original:
            log.info("dropping manual 'see also' list in %s user docs: '%s'", doc.filename, original)
        newdoc = deepcopy(doc)
        newdoc.userdoc=          doc.userdoc[:secstart] + \
            "\n" + ", ".join([":doc:`{taglabel} <index_{tag}>`".format(tag=tag, taglabel=rightcase(tag)) \
                             for tag in doc.keywords]) + "\n\n" + \
            doc.userdoc[secend:]
        return newdoc
    raise ValueError("No section '%s' found in %s!" % (see_also, doc.filename))


def write_rst_output(doc, newprefix="output/", newsuffix=".rst"):
    """
    Write raw rst to a file and generate a wrapper with index

    Parameters
    ----------
    doc: DocMeta
        userdoc instance to modify
    """
    outfile = Path(newprefix) / doc.filename.with_suffix(newsuffix).name
    log.debug("write_rst_file: output to %s", outfile)
    with outfile.open("w") as outfile:
        outfile.write(doc.userdoc)


def make_hierarchy(tags, *basetags):
    """
    This method adds a single level of hierachy to the given dictionary.

    First a list of items with given basetags is created (intersection). Then
    this list is subdivided into sections by creating intersections with all
    remaining tags.

    Parameters
    ----------
    tags : dict
       flat dictionary of tag to entry

    basetags : iterable
       iterable of a subset of tags.keys(), if no basetags are given the
       original tags list is returned unmodified.

    Returns
    -------

    dict
       A hierarchical dictionary of (dict or set) with items in the
       intersection of basetag.
    """
    if not basetags:
        return tags

    # items having all given basetags
    baseitems = set.intersection(*[set(items) for tag, items in tags.items() if tag in basetags])
    tree = dict()
    subtags = [t for t in tags.keys() if t not in basetags]
    for subtag in subtags:
        docs = set(tags[subtag]).intersection(baseitems)
        if docs:
            tree[subtag] = docs
    remaining = None
    if tree.values():
        remaining = baseitems.difference(set.union(*tree.values()))
    if remaining:
        tree[''] = remaining
    return {basetags: tree}


def rst_index(hierarchy, current_tags=[], underlines='=-~', top=True):
    """
    Create an index page from a given hierarchical dict of documents.

    The given `hierarchy` is pretty-printed and returned as a string.

    Parameters
    ----------
    hierarchy : dict
       dictionary or dict-of-dict returned from `make_hierarchy()`

    current_tags : list
       applied filters for the current index (parameters given to
       `make_hierarchy()`. Defaults to `[]`, which doesn't display any filters.

    underlines : iterable
       list of characters to use for underlining deeper levels of the generated
       index.

    top : bool
       optional argument keeping track of recursive calls. Calls from within
       `rst_index` itself will always call with `top=False`.

    Returns
    -------

    str
       formatted pretty index.
    """
    def mktitle(t, ul, link=None):
        text = t
        if t != t.upper():
            text = t.title()  # title-case any tag that is not an acronym
        title = ':doc:`{text} <{filename}>`'.format(
            text=text,
            filename=link or "index_"+t)
        text = title+'\n'+ul*len(title)+'\n\n'
        return text

    def mkitem(t):
        return "* :doc:`%s`" % os.path.splitext(t)[0]

    output = list()
    if top:
        # Prevent warnings by adding an orphan role so Sphinx does not expect it in toctrees
        orphan_text = ":orphan:" + "\n\n"
        page_title = "Model directory"
        description = """
                       The model directory is organized and autogenerated by keywords (e.g., adaptive threshold,
                       conductance-based etc.). Models that contain a specific keyword will be listed under that word.
                       For more information on models, see our :ref:`intro to NEST models <modelsmain>`.
                       """
        if len(hierarchy.keys()) == 1:
            page_title += ": " + ", ".join(current_tags)
        output.append(orphan_text + page_title)
        output.append(underlines[0]*len(page_title)+"\n")
        output.append(description + "\n")
        if len(hierarchy.keys()) != 1:
            underlines = underlines[1:]

    for tags, items in sorted(hierarchy.items()):

        if "NOINDEX" in tags:
            continue
        if isinstance(tags, str):
            title = tags
        else:
            title = " & ".join(tags)
        if title and not len(hierarchy) == 1:   # not print title if already selected by current_tags
            output.append(mktitle(title, underlines[0]))
        if isinstance(items, dict):
            output.append(rst_index(items, current_tags, underlines[1:], top=False))
        else:
            for item in sorted(items):
                output.append(mkitem(item))
            output.append("")
    return "\n".join(output)


def reverse_dict(tags):
    """
    Return the reversed dict-of-list

    Given a dictionary `keys:values`, this function creates the inverted
    dictionary `value:[key, key2, ...]` with one entry per value of the given
    dict. Since many keys can have the same value, the reversed dict must have
    list-of-keys as values.

    Parameters
    ----------

    tags : dict
       Values must be hashable to be used as keys for the result.

    Returns
    -------

    dict
       Mapping the original values to lists of original keys.
    """
    revdict = dict()
    for tag, items in tags.items():
        for item in items:
            revdict.setdefault(item, list()).append(tag)
    return revdict


def CreateTagIndices(tags, outdir="userdocs/"):
    """
    This function generates all combinations of tags and creates an index page
    for each combination using `rst_index`.

    Parameters
    ----------

    tags : dict
       dictionary of tags

    outdir : str, path
       path to the intended output directory (handed to `rst_index`.

    Returns
    -------

    list
        list of names of generated files.
    """
    taglist = list(tags.keys())
    indexfiles = list()
    depth = min(4, len(taglist))    # how many levels of indices to create at most
    nindices = sum([comb(len(taglist), L) for L in range(depth-1)])
    log.info("indices down to level %d → %d possible keyword combinations", depth, nindices)
    for current_tags in tqdm(chain(*[combinations(taglist, L) for L in range(depth-1)]), unit="idx",
                             desc="keyword indices", total=nindices):
        current_tags = sorted(current_tags)
        indexname = "index%s.rst" % "".join(["_"+x for x in current_tags])
        hier = make_hierarchy(tags.copy(), *current_tags)
        if not any(hier.values()):
            log.debug("index %s is empyt!", str(current_tags))
            continue
        nfiles = len(set.union(*chain([set(subtag) for subtag in hier.values()])))
        log.debug("generating index for %s...", str(current_tags))
        indextext = rst_index(hier, current_tags)
        with open(os.path.join(outdir, indexname), 'w') as outfile:
            outfile.write(indextext)
        indexfiles.append(indexname)
    log.info("%4d non-empty index files generated", len(indexfiles))
    return indexfiles


class JsonWriter:
    """
    Helper class to have a unified data output interface.
    """
    def __init__(self, outdir):
        self.outdir = outdir
        log.info("writing JSON files to %s", self.outdir)

    def write(self, obj, name):
        """
        Store the given object with the given name.
        """
        outname = os.path.join(self.outdir, name + ".json")
        with open(outname, 'w') as outfile:
            json.dump(obj, outfile)
            log.info("data saved as " + outname)


def getTitles(text):
    '''
    extract all sections from the given RST file

    Parameters
    ----------

    text : str
      restructuredtext user documentation

    Returns
    -------

    list
      elements are the section title re.match objects
    '''
    titlechar = r'\+'
    title_re = re.compile(r'^(?P<title>.+)\n(?P<underline>'+titlechar+r'+)$', re.MULTILINE)
    titles = []
    # extract all titles
    for match in title_re.finditer(text):
        log.debug("MATCH from %s to %s: %s", match.start(), match.end(), pformat(match.groupdict()))
        if len(match.group('title')) != len(match.group('underline')):
            log.warning("Length of section title '%s' (%d) does not match length of underline (%d)",
                        match.group('title'),
                        len(match.group('title')),
                        len(match.group('underline')))
        titles.append(match)
    return titles


def ExtractUserDocs(listoffiles, basedir='..', outdir='userdocs/'):
    """
    Extract and build all user documentation and build tag indices.

    Writes extracted information to JSON files in outdir. In particular the
    list of seen tags mapped to files they appear in, and the indices generated
    from all combinations of tags.

    Parameters are the same as for `UserDocExtractor` and are handed to it
    unmodified.

    Returns
    -------

    None
    """
    data = JsonWriter(outdir)
    # Gather all information and write RSTs
    tags = UserDocExtractor(listoffiles, basedir=basedir, outdir=outdir)
    data.write(tags, "tags")

    indexfiles = CreateTagIndices(tags, outdir=outdir)
    data.write(indexfiles, "indexfiles")

    toc_list = [name[:-4] for names in tags.values() for name in names]
    idx_list = [indexfile[:-4] for indexfile in indexfiles]

    with open(os.path.join(outdir, "toc-tree.json"), "w") as tocfile:
        json.dump(list(set(toc_list)) + list(set(idx_list)), tocfile)


def sourcefiles(*globs, basedir=os.curdir, excludes=None):
    excludes = excludes or ['*.swp', '.git', 'venv', 'conda', '_doxygen', 'build']
    for path, dirs, names in os.walk(basedir):
        path = Path(path)
        log.debug("%s", path)
        removedirs = set(chain.from_iterable((fnfilter(dirs, pattern) for pattern in excludes)))
        if removedirs:
            log.debug("ignoring %s", removedirs)
        for name in removedirs:
            dirs.remove(name)
        for name in names:
            if any([fnmatch(name, pat) for pat in excludes]):       # reject excludes
                continue
            if not any([fnmatch(name, pat) for pat in globs]):      # reject not matching any globs
                continue
            if (path / name).is_file():
                yield path / name



def renderpages(filenames):
    steps = [
        DocMeta,
        rewrite_short_description,
        rewrite_see_also,
        write_rst_output,
    ]

    for filename in filenames:
        item = [filename]
        for step in steps:
            try:
                item = [step(*item)]
            except ValueError as exc:
                log.warning("Could not run %s on %s:", step.__name__, filename)
                log.exception(exc)
                break

    #for filename in filenames:
    #    meta = DocMeta(filename)
    #    newdoc = meta.userdoc
    #    try:
    #        newdoc = rewrite_short_description(newdoc, filename)
    #    except ValueError as e:
    #        log.warning("Documentation added unfixed: %s", e)
    #    try:
    #        newdoc = rewrite_see_also(newdoc, filename, tags)
    #    except ValueError as e:
    #        log.info("Failed to rebuild 'See also' section: %s", e)

    #    outfile = Path("output") / filename.with_suffix(".rst").name
    #    write_rst_files(doc, tags, outfile)


def main():
    inputfiles = ['source/**/*.h', 'source/**/*.py']
    #inputfiles = ["models/*.h", "nestkernel/*.h"]

    index = TagIndex()

    def scanfiles():
        yield from sourcefiles("*.py", "*.h", "*.cxx", basedir = "../..")
    index.scan_files(scanfiles())

    renderpages(scanfiles())


if __name__ == '__main__':
    main()
    #ExtractUserDocs(
    #    outdir="userdocs/"
    #)
