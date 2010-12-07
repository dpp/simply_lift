#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# Alex 20090308
# eLyXer main script
# http://www.nongnu.org/elyxer/


import sys
import os.path




import os.path



import sys
import codecs



import sys

class Trace(object):
  "A tracing class"

  debugmode = False
  quietmode = False
  showlinesmode = False

  prefix = None

  def debug(cls, message):
    "Show a debug message"
    if not Trace.debugmode or Trace.quietmode:
      return
    Trace.show(message, sys.stdout)

  def message(cls, message):
    "Show a trace message"
    if Trace.quietmode:
      return
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stdout)

  def error(cls, message):
    "Show an error message"
    message = '* ' + message
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stderr)

  def fatal(cls, message):
    "Show an error message and terminate"
    Trace.error('FATAL: ' + message)
    exit(-1)

  def show(cls, message, channel):
    "Show a message out of a channel"
    message = message.encode('utf-8')
    channel.write(message + '\n')

  debug = classmethod(debug)
  message = classmethod(message)
  error = classmethod(error)
  fatal = classmethod(fatal)
  show = classmethod(show)



class LineReader(object):
  "Reads a file line by line"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
    else:
      self.file = codecs.open(filename, 'rU', 'utf-8')
    self.linenumber = 1
    self.lastline = None
    self.current = None
    self.mustread = True
    self.depleted = False
    try:
      self.readline()
    except UnicodeDecodeError:
      # try compressed file
      import gzip
      self.file = gzip.open(filename, 'rb')
      self.readline()

  def setstart(self, firstline):
    "Set the first line to read."
    for i in range(firstline):
      self.file.readline()
    self.linenumber = firstline

  def setend(self, lastline):
    "Set the last line to read."
    self.lastline = lastline

  def currentline(self):
    "Get the current line"
    if self.mustread:
      self.readline()
    return self.current

  def nextline(self):
    "Go to next line"
    if self.depleted:
      Trace.fatal('Read beyond file end')
    self.mustread = True

  def readline(self):
    "Read a line from file"
    self.current = self.file.readline()
    if not isinstance(self.file, codecs.StreamReaderWriter):
      self.current = self.current.decode('utf-8')
    if len(self.current) == 0:
      self.depleted = True
    self.current = self.current.rstrip('\n\r')
    self.linenumber += 1
    self.mustread = False
    Trace.prefix = 'Line ' + unicode(self.linenumber) + ': '
    if self.linenumber % 1000 == 0:
      Trace.message('Parsing')

  def finished(self):
    "Find out if the file is finished"
    if self.lastline and self.linenumber == self.lastline:
      return True
    if self.mustread:
      self.readline()
    return self.depleted

  def close(self):
    self.file.close()

class LineWriter(object):
  "Writes a file as a series of lists"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
      self.filename = None
    else:
      self.file = codecs.open(filename, 'w', "utf-8")
      self.filename = filename

  def write(self, strings):
    "Write a list of strings"
    for string in strings:
      if not isinstance(string, basestring):
        Trace.error('Not a string: ' + unicode(string) + ' in ' + unicode(strings))
        return
      self.writestring(string)

  def writestring(self, string):
    "Write a string"
    if self.file == sys.stdout:
      string = string.encode('utf-8')
    self.file.write(string)

  def writeline(self, line):
    "Write a line to file"
    self.writestring(line + '\n')

  def close(self):
    self.file.close()




import codecs
import os.path



import codecs


class BibStylesConfig(object):
  "Configuration class from config file"

  abbrvnat = {
      
      u'@article':u'$author. $title. <i>$journal</i>,{ {$volume:}$pages,} $month $year.{ doi: $doi.}{ URL <a href="$url">$url</a>.}', 
      u'cite':[u'$surname($year)',u'$rest',], 
      u'default':u'$author. <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      }

  authordate2 = {
      
      u'@article':u'$author. $year. $title. <i>$journal</i>, <b>$volume</b>($number), $pages.{ URL <a href="$url">$url</a>.}', 
      u'@book':u'$author. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}', 
      u'cite':[u'$surname',u' $year; $rest',], 
      u'default':u'$author. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}', 
      }

  default = {
      
      u'@article':u'$author, “$title”, <i>$journal</i>, pp. $pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@book':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@booklet':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@conference':u'$author, “$title”, <i>$journal</i>, pp. $pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@inbook':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@incollection':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@inproceedings':u'$author, “$title”, <i>$journal</i>, pp. $pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@manual':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@mastersthesis':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@misc':u'$author, <i>$title</i>.{ $publisher,}{ $howpublished,} $year.{ URL <a href="$url">$url</a>.}', 
      u'@phdthesis':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'@proceedings':u'$author, “$title”, <i>$journal</i>, pp. $pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@techreport':u'$author, <i>$title</i>, $year.{ URL <a href="$url">$url</a>.}', 
      u'@unpublished':u'$author, “$title”, <i>$journal</i>, $year.{ URL <a href="$url">$url</a>.}', 
      u'cite':[u'$index',u'$rest',], 
      u'default':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      }

  ieeetr = {
      
      u'@article':u'$author, “$title”, <i>$journal</i>, vol. $volume, no. $number, pp. $pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@book':u'$author, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      u'cite':[u'$index',u'$rest',], 
      u'default':u'$author, “$title”. $year.{ URL <a href="$url">$url</a>.}', 
      }

  plain = {
      
      u'@article':u'$author. $title. <i>$journal</i>, $volumen($number):$pages, $year.{ URL <a href="$url">$url</a>.}', 
      u'@book':u'$author. <i>$title</i>. $publisher, $month $year.{ URL <a href="$url">$url</a>.}', 
      u'cite':[u'$index',u'$rest',], 
      u'default':u'$author. <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}', 
      }

  vancouver = {
      
      u'@article':u'$author. $title. <i>$journal</i>, $year;<b>$volume</b>($number):$pages.{ Available from: <a href="$url">$url</a>.}', 
      u'@book':u'$author. $title. {$publisher, }$year.{ Available from: <a href="$url">$url</a>.}', 
      u'cite':[u'$index',u'$rest',], 
      u'default':u'$author. $title; {$publisher, }$year.{ $howpublished.}{ Available from: <a href="$url">$url</a>.}', 
      }

class BibTeXConfig(object):
  "Configuration class from config file"

  escaped = {
      u'--':u'—', u'..':u'.', u'\\"a':u'ä', u'\\"e':u'ë', u'\\"i':u'ï', 
      u'\\"o':u'ö', u'\\"u':u'ü', 
      }

class ContainerConfig(object):
  "Configuration class from config file"

  endings = {
      u'Align':u'\\end_layout', u'BarredText':u'\\bar', 
      u'BoldText':u'\\series', u'Cell':u'</cell', u'ColorText':u'\\color', 
      u'EmphaticText':u'\\emph', u'Hfill':u'\\hfill', u'Inset':u'\\end_inset', 
      u'Layout':u'\\end_layout', u'LyXFooter':u'\\end_document', 
      u'LyXHeader':u'\\end_header', u'Row':u'</row', u'ShapedText':u'\\shape', 
      u'SizeText':u'\\size', u'TextFamily':u'\\family', 
      u'VersalitasText':u'\\noun', 
      }

  startendings = {
      u'\\begin_deeper':u'\\end_deeper', u'\\begin_inset':u'\\end_inset', 
      u'\\begin_layout':u'\\end_layout', 
      }

  starts = {
      u'':u'StringContainer', u'#LyX':u'BlackBox', u'</lyxtabular':u'BlackBox', 
      u'<cell':u'Cell', u'<column':u'Column', u'<row':u'Row', 
      u'\\align':u'Align', u'\\bar':u'BarredText', 
      u'\\bar default':u'BlackBox', u'\\bar no':u'BlackBox', 
      u'\\begin_body':u'BlackBox', u'\\begin_deeper':u'DeeperList', 
      u'\\begin_document':u'BlackBox', u'\\begin_header':u'LyXHeader', 
      u'\\begin_inset Box':u'BoxInset', u'\\begin_inset Branch':u'Branch', 
      u'\\begin_inset Caption':u'Caption', 
      u'\\begin_inset CommandInset bibitem':u'BiblioEntry', 
      u'\\begin_inset CommandInset bibtex':u'BibTeX', 
      u'\\begin_inset CommandInset citation':u'BiblioCitation', 
      u'\\begin_inset CommandInset href':u'URL', 
      u'\\begin_inset CommandInset include':u'IncludeInset', 
      u'\\begin_inset CommandInset index_print':u'PrintIndex', 
      u'\\begin_inset CommandInset label':u'Label', 
      u'\\begin_inset CommandInset nomencl_print':u'PrintNomenclature', 
      u'\\begin_inset CommandInset nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset CommandInset ref':u'Reference', 
      u'\\begin_inset CommandInset toc':u'TableOfContents', 
      u'\\begin_inset ERT':u'ERT', u'\\begin_inset Flex':u'FlexInset', 
      u'\\begin_inset Flex Chunkref':u'NewfangledChunkRef', 
      u'\\begin_inset Flex Marginnote':u'SideNote', 
      u'\\begin_inset Flex Sidenote':u'SideNote', 
      u'\\begin_inset Flex URL':u'FlexURL', u'\\begin_inset Float':u'Float', 
      u'\\begin_inset FloatList':u'ListOf', u'\\begin_inset Foot':u'Footnote', 
      u'\\begin_inset Formula':u'Formula', 
      u'\\begin_inset FormulaMacro':u'FormulaMacro', 
      u'\\begin_inset Graphics':u'Image', u'\\begin_inset Index':u'IndexEntry', 
      u'\\begin_inset Info':u'InfoInset', 
      u'\\begin_inset LatexCommand bibitem':u'BiblioEntry', 
      u'\\begin_inset LatexCommand bibtex':u'BibTeX', 
      u'\\begin_inset LatexCommand cite':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citealt':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citep':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citet':u'BiblioCitation', 
      u'\\begin_inset LatexCommand htmlurl':u'URL', 
      u'\\begin_inset LatexCommand index':u'IndexEntry', 
      u'\\begin_inset LatexCommand label':u'Label', 
      u'\\begin_inset LatexCommand nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset LatexCommand prettyref':u'Reference', 
      u'\\begin_inset LatexCommand printindex':u'PrintIndex', 
      u'\\begin_inset LatexCommand printnomenclature':u'PrintNomenclature', 
      u'\\begin_inset LatexCommand ref':u'Reference', 
      u'\\begin_inset LatexCommand tableofcontents':u'TableOfContents', 
      u'\\begin_inset LatexCommand url':u'URL', 
      u'\\begin_inset LatexCommand vref':u'Reference', 
      u'\\begin_inset Marginal':u'SideNote', 
      u'\\begin_inset Newline':u'NewlineInset', 
      u'\\begin_inset Newpage':u'NewPageInset', u'\\begin_inset Note':u'Note', 
      u'\\begin_inset OptArg':u'ShortTitle', 
      u'\\begin_inset Quotes':u'QuoteContainer', 
      u'\\begin_inset Tabular':u'Table', u'\\begin_inset Text':u'InsetText', 
      u'\\begin_inset VSpace':u'VerticalSpace', u'\\begin_inset Wrap':u'Wrap', 
      u'\\begin_inset listings':u'Listing', u'\\begin_inset space':u'Space', 
      u'\\begin_layout':u'Layout', u'\\begin_layout Abstract':u'Abstract', 
      u'\\begin_layout Author':u'Author', 
      u'\\begin_layout Bibliography':u'Bibliography', 
      u'\\begin_layout Chunk':u'NewfangledChunk', 
      u'\\begin_layout Description':u'Description', 
      u'\\begin_layout Enumerate':u'ListItem', 
      u'\\begin_layout Itemize':u'ListItem', u'\\begin_layout List':u'List', 
      u'\\begin_layout LyX-Code':u'LyXCode', 
      u'\\begin_layout Plain':u'PlainLayout', 
      u'\\begin_layout Standard':u'StandardLayout', 
      u'\\begin_layout Title':u'Title', u'\\color':u'ColorText', 
      u'\\color inherit':u'BlackBox', u'\\color none':u'BlackBox', 
      u'\\emph default':u'BlackBox', u'\\emph off':u'BlackBox', 
      u'\\emph on':u'EmphaticText', u'\\emph toggle':u'EmphaticText', 
      u'\\end_body':u'LyXFooter', u'\\family':u'TextFamily', 
      u'\\family default':u'BlackBox', u'\\family roman':u'BlackBox', 
      u'\\hfill':u'Hfill', u'\\labelwidthstring':u'BlackBox', 
      u'\\lang':u'LangLine', u'\\length':u'BlackBox', 
      u'\\lyxformat':u'LyXFormat', u'\\lyxline':u'LyXLine', 
      u'\\newline':u'Newline', u'\\newpage':u'NewPage', 
      u'\\noindent':u'BlackBox', u'\\noun default':u'BlackBox', 
      u'\\noun off':u'BlackBox', u'\\noun on':u'VersalitasText', 
      u'\\paragraph_spacing':u'BlackBox', u'\\series bold':u'BoldText', 
      u'\\series default':u'BlackBox', u'\\series medium':u'BlackBox', 
      u'\\shape':u'ShapedText', u'\\shape default':u'BlackBox', 
      u'\\shape up':u'BlackBox', u'\\size':u'SizeText', 
      u'\\size normal':u'BlackBox', u'\\start_of_appendix':u'Appendix', 
      }

  string = {
      u'startcommand':u'\\', 
      }

  table = {
      u'headers':[u'<lyxtabular',u'<features',], 
      }

class EscapeConfig(object):
  "Configuration class from config file"

  chars = {
      u'\n':u'', u' -- ':u' — ', u'\'':u'’', u'---':u'—', u'`':u'‘', 
      }

  commands = {
      u'\\InsetSpace \\space{}':u' ', u'\\InsetSpace \\thinspace{}':u' ', 
      u'\\InsetSpace ~':u' ', u'\\SpecialChar \\-':u'', 
      u'\\SpecialChar \\@.':u'.', u'\\SpecialChar \\ldots{}':u'…', 
      u'\\SpecialChar \\menuseparator':u' ▷ ', 
      u'\\SpecialChar \\nobreakdash-':u'-', u'\\SpecialChar \\slash{}':u'/', 
      u'\\SpecialChar \\textcompwordmark{}':u'', u'\\backslash':u'\\', 
      }

  entities = {
      u'&':u'&amp;', u'<':u'&lt;', u'>':u'&gt;', 
      }

  html = {
      u'/>':u'>', 
      }

  iso885915 = {
      u' ':u'&nbsp;', u' ':u'&emsp;', u' ':u'&#8197;', 
      }

  nonunicode = {
      u' ':u' ', 
      }

class FileConfig(object):
  "Configuration class from config file"

  parsing = {
      u'encodings':[u'utf-8',u'Cp1252',], 
      }

class FootnoteConfig(object):
  "Configuration class from config file"

  constants = {
      u'postfrom':u'] ', u'postto':u'→] ', u'prefrom':u'[→', u'preto':u' [', 
      }

class FormulaConfig(object):
  "Configuration class from config file"

  alphacommands = {
      u'\\AA':u'Å', u'\\AE':u'Æ', u'\\L':u'Ł', u'\\O':u'Ø', u'\\OE':u'Œ', 
      u'\\aa':u'å', u'\\ae':u'æ', u'\\alpha':u'α', u'\\beta':u'β', 
      u'\\delta':u'δ', u'\\epsilon':u'ϵ', u'\\eta':u'η', u'\\gamma':u'γ', 
      u'\\iota':u'ι', u'\\kappa':u'κ', u'\\l':u'ł', u'\\lambda':u'λ', 
      u'\\mu':u'μ', u'\\nu':u'ν', u'\\o':u'ø', u'\\oe':u'œ', u'\\omega':u'ω', 
      u'\\phi':u'φ', u'\\pi':u'π', u'\\psi':u'ψ', u'\\rho':u'ρ', 
      u'\\sigma':u'σ', u'\\ss':u'ß', u'\\tau':u'τ', u'\\textcrh':u'ħ', 
      u'\\theta':u'θ', u'\\upsilon':u'υ', u'\\varDelta':u'∆', 
      u'\\varGamma':u'Γ', u'\\varLambda':u'Λ', u'\\varOmega':u'Ω', 
      u'\\varPhi':u'Φ', u'\\varPi':u'Π', u'\\varPsi':u'Ψ', u'\\varSigma':u'Σ', 
      u'\\varTheta':u'Θ', u'\\varUpsilon':u'Υ', u'\\varXi':u'Ξ', 
      u'\\varepsilon':u'ε', u'\\varkappa':u'ϰ', u'\\varphi':u'φ', 
      u'\\varpi':u'ϖ', u'\\varrho':u'ϱ', u'\\varsigma':u'ς', 
      u'\\vartheta':u'ϑ', u'\\xi':u'ξ', u'\\zeta':u'ζ', 
      }

  array = {
      u'begin':u'\\begin', u'cellseparator':u'&', u'end':u'\\end', 
      u'rowseparator':u'\\\\', 
      }

  commands = {
      u'\\ ':u' ', u'\\!':u'', u'\\$':u'$', u'\\%':u'%', u'\\,':u' ', 
      u'\\:':u' ', u'\\;':u' ', u'\\APLdownarrowbox':u'⍗', 
      u'\\APLleftarrowbox':u'⍇', u'\\APLrightarrowbox':u'⍈', 
      u'\\APLuparrowbox':u'⍐', u'\\Box':u'□', u'\\Bumpeq':u'≎', 
      u'\\CIRCLE':u'●', u'\\Cap':u'⋒', u'\\CheckedBox':u'☑', u'\\Circle':u'○', 
      u'\\Coloneqq':u'⩴', u'\\Corresponds':u'≙', u'\\Cup':u'⋓', 
      u'\\Delta':u'Δ', u'\\Diamond':u'◇', u'\\Downarrow':u'⇓', u'\\EUR':u'€', 
      u'\\Gamma':u'Γ', u'\\Im':u'ℑ', u'\\Join':u'⨝', u'\\LEFTCIRCLE':u'◖', 
      u'\\LEFTcircle':u'◐', u'\\Lambda':u'Λ', u'\\Leftarrow':u'⇐', 
      u'\\Leftrightarrow':u' ⇔ ', u'\\Lleftarrow':u'⇚', 
      u'\\Longleftarrow':u'⟸', u'\\Longleftrightarrow':u'⟺', 
      u'\\Longrightarrow':u'⟹', u'\\Lsh':u'↰', u'\\Mapsfrom':u'⇐|', 
      u'\\Mapsto':u'|⇒', u'\\Omega':u'Ω', u'\\P':u'¶', u'\\Phi':u'Φ', 
      u'\\Pi':u'Π', u'\\Pr':u'Pr', u'\\Psi':u'Ψ', u'\\RIGHTCIRCLE':u'◗', 
      u'\\RIGHTcircle':u'◑', u'\\Re':u'ℜ', u'\\Rightarrow':u' ⇒ ', 
      u'\\Rrightarrow':u'⇛', u'\\Rsh':u'↱', u'\\S':u'§', u'\\Sigma':u'Σ', 
      u'\\Square':u'☐', u'\\Subset':u'⋐', u'\\Supset':u'⋑', u'\\Theta':u'Θ', 
      u'\\Uparrow':u'⇑', u'\\Updownarrow':u'⇕', u'\\Upsilon':u'Υ', 
      u'\\Vdash':u'⊩', u'\\Vert':u'∥', u'\\Vvdash':u'⊪', u'\\XBox':u'☒', 
      u'\\Xi':u'Ξ', u'\\Yup':u'⅄', u'\\\\':u'<br/>', u'\\_':u'_', 
      u'\\aleph':u'ℵ', u'\\amalg':u'∐', u'\\angle':u'∠', u'\\approx':u' ≈ ', 
      u'\\aquarius':u'♒', u'\\arccos':u'arccos', u'\\arcsin':u'arcsin', 
      u'\\arctan':u'arctan', u'\\arg':u'arg', u'\\aries':u'♈', u'\\ast':u'∗', 
      u'\\asymp':u'≍', u'\\backepsilon':u'∍', u'\\backprime':u'‵', 
      u'\\backsimeq':u'⋍', u'\\backslash':u'\\', u'\\barwedge':u'⊼', 
      u'\\because':u'∵', u'\\beth':u'ℶ', u'\\between':u'≬', u'\\bigcap':u'∩', 
      u'\\bigcirc':u'○', u'\\bigcup':u'∪', u'\\bigodot':u'⊙', 
      u'\\bigoplus':u'⊕', u'\\bigotimes':u'⊗', u'\\bigsqcup':u'⊔', 
      u'\\bigstar':u'★', u'\\bigtriangledown':u'▽', u'\\bigtriangleup':u'△', 
      u'\\biguplus':u'⊎', u'\\bigvee':u'∨', u'\\bigwedge':u'∧', 
      u'\\blacklozenge':u'⧫', u'\\blacksmiley':u'☻', u'\\blacksquare':u'■', 
      u'\\blacktriangle':u'▲', u'\\blacktriangledown':u'▼', 
      u'\\blacktriangleright':u'▶', u'\\bot':u'⊥', u'\\bowtie':u'⋈', 
      u'\\box':u'▫', u'\\boxdot':u'⊡', u'\\bullet':u'•', u'\\bumpeq':u'≏', 
      u'\\cancer':u'♋', u'\\cap':u'∩', u'\\capricornus':u'♑', u'\\cdot':u'⋅', 
      u'\\cdots':u'⋯', u'\\centerdot':u'∙', u'\\checkmark':u'✓', u'\\chi':u'χ', 
      u'\\circ':u'○', u'\\circeq':u'≗', u'\\circledR':u'®', 
      u'\\circledast':u'⊛', u'\\circledcirc':u'⊚', u'\\circleddash':u'⊝', 
      u'\\clubsuit':u'♣', u'\\coloneqq':u'≔', u'\\complement':u'∁', 
      u'\\cong':u'≅', u'\\coprod':u'∐', u'\\copyright':u'©', u'\\cos':u'cos', 
      u'\\cosh':u'cosh', u'\\cot':u'cot', u'\\coth':u'coth', u'\\csc':u'csc', 
      u'\\cup':u'∪', u'\\curvearrowleft':u'↶', u'\\curvearrowright':u'↷', 
      u'\\dag':u'†', u'\\dagger':u'†', u'\\daleth':u'ℸ', 
      u'\\dashleftarrow':u'⇠', u'\\dashrightarrow':u' ⇢ ', u'\\dashv':u'⊣', 
      u'\\ddag':u'‡', u'\\ddagger':u'‡', u'\\ddots':u'⋱', u'\\deg':u'deg', 
      u'\\det':u'det', u'\\diagdown':u'╲', u'\\diagup':u'╱', u'\\diamond':u'◇', 
      u'\\diamondsuit':u'♦', u'\\dim':u'dim', u'\\displaystyle':u'', 
      u'\\div':u'÷', u'\\divideontimes':u'⋇', u'\\dotdiv':u'∸', 
      u'\\doteq':u'≐', u'\\doteqdot':u'≑', u'\\dotplus':u'∔', u'\\dots':u'…', 
      u'\\doublebarwedge':u'⌆', u'\\downarrow':u'↓', u'\\downdownarrows':u'⇊', 
      u'\\downharpoonleft':u'⇃', u'\\downharpoonright':u'⇂', u'\\earth':u'♁', 
      u'\\ell':u'ℓ', u'\\emptyset':u'∅', u'\\eqcirc':u'≖', u'\\eqcolon':u'≕', 
      u'\\eqsim':u'≂', u'\\equiv':u' ≡ ', u'\\euro':u'€', u'\\exists':u'∃', 
      u'\\exp':u'exp', u'\\fallingdotseq':u'≒', u'\\female':u'♀', 
      u'\\flat':u'♭', u'\\forall':u'∀', u'\\frown':u'⌢', u'\\frownie':u'☹', 
      u'\\gcd':u'gcd', u'\\ge':u' ≥ ', u'\\gemini':u'♊', u'\\geq':u' ≥ ', 
      u'\\geq)':u'≥', u'\\geqq':u'≧', u'\\geqslant':u'≥', u'\\gets':u'←', 
      u'\\gg':u'≫', u'\\ggg':u'⋙', u'\\gimel':u'ℷ', u'\\gneqq':u'≩', 
      u'\\gnsim':u'⋧', u'\\gtrdot':u'⋗', u'\\gtreqless':u'⋚', 
      u'\\gtreqqless':u'⪌', u'\\gtrless':u'≷', u'\\gtrsim':u'≳', 
      u'\\hbar':u'ℏ', u'\\heartsuit':u'♥', 
      u'\\hfill':u'<span class="hfill"> </span>', u'\\hom':u'hom', 
      u'\\hookleftarrow':u'↩', u'\\hookrightarrow':u'↪', u'\\hslash':u'ℏ', 
      u'\\idotsint':u'∫⋯∫', u'\\iiint':u'∭', u'\\iint':u'∬', u'\\imath':u'ı', 
      u'\\implies':u'  ⇒  ', u'\\in':u' ∈ ', u'\\inf':u'inf', u'\\infty':u'∞', 
      u'\\int':u'<span class="bigsymbol">∫</span>', 
      u'\\intop':u'<span class="bigsymbol">∫</span>', u'\\invneg':u'⌐', 
      u'\\jmath':u'ȷ', u'\\jupiter':u'♃', u'\\ker':u'ker', u'\\land':u'∧', 
      u'\\landupint':u'∱', u'\\langle':u'⟨', u'\\lbrace':u'{', 
      u'\\lbrace)':u'{', u'\\lbrack':u'[', u'\\lceil':u'⌈', u'\\ldots':u'…', 
      u'\\le':u'≤', u'\\leadsto':u'⇝', u'\\leftarrow':u' ← ', 
      u'\\leftarrow)':u'←', u'\\leftarrowtail':u'↢', u'\\leftarrowtobar':u'⇤', 
      u'\\leftharpoondown':u'↽', u'\\leftharpoonup':u'↼', 
      u'\\leftleftarrows':u'⇇', u'\\leftleftharpoons':u'⥢', u'\\leftmoon':u'☾', 
      u'\\leftrightarrow':u'↔', u'\\leftrightarrows':u'⇆', 
      u'\\leftrightharpoons':u'⇋', u'\\leftthreetimes':u'⋋', u'\\leo':u'♌', 
      u'\\leq':u' ≤ ', u'\\leq)':u'≤', u'\\leqq':u'≦', u'\\leqslant':u'≤', 
      u'\\lessdot':u'⋖', u'\\lesseqgtr':u'⋛', u'\\lesseqqgtr':u'⪋', 
      u'\\lessgtr':u'≶', u'\\lesssim':u'≲', u'\\lfloor':u'⌊', u'\\lg':u'lg', 
      u'\\lhd':u'⊲', u'\\libra':u'♎', u'\\lightning':u'↯', u'\\lim':u'lim', 
      u'\\liminf':u'liminf', u'\\limsup':u'limsup', u'\\ll':u'≪', 
      u'\\lll':u'⋘', u'\\ln':u'ln', u'\\lneqq':u'≨', u'\\lnot':u'¬', 
      u'\\lnsim':u'⋦', u'\\log':u'log', u'\\longleftarrow':u'⟵', 
      u'\\longleftrightarrow':u'⟷', u'\\longmapsto':u'⟼', 
      u'\\longrightarrow':u'⟶', u'\\looparrowleft':u'↫', 
      u'\\looparrowright':u'↬', u'\\lor':u'∨', u'\\lozenge':u'◊', 
      u'\\ltimes':u'⋉', u'\\lyxlock':u'', u'\\male':u'♂', u'\\maltese':u'✠', 
      u'\\mapsfrom':u'↤', u'\\mapsto':u'↦', u'\\mathcircumflex':u'^', 
      u'\\max':u'max', u'\\measuredangle':u'∡', u'\\mercury':u'☿', 
      u'\\mho':u'℧', u'\\mid':u'∣', u'\\min':u'min', u'\\models':u'⊨', 
      u'\\mp':u'∓', u'\\multimap':u'⊸', u'\\nLeftarrow':u'⇍', 
      u'\\nLeftrightarrow':u'⇎', u'\\nRightarrow':u'⇏', u'\\nVDash':u'⊯', 
      u'\\nabla':u'∇', u'\\napprox':u'≉', u'\\natural':u'♮', u'\\ncong':u'≇', 
      u'\\ne':u' ≠ ', u'\\nearrow':u'↗', u'\\neg':u'¬', u'\\neg)':u'¬', 
      u'\\neptune':u'♆', u'\\neq':u' ≠ ', u'\\nequiv':u'≢', u'\\nexists':u'∄', 
      u'\\ngeqslant':u'≱', u'\\ngtr':u'≯', u'\\ngtrless':u'≹', u'\\ni':u'∋', 
      u'\\ni)':u'∋', u'\\nleftarrow':u'↚', u'\\nleftrightarrow':u'↮', 
      u'\\nleqslant':u'≰', u'\\nless':u'≮', u'\\nlessgtr':u'≸', u'\\nmid':u'∤', 
      u'\\nonumber':u'', u'\\not':u'¬', u'\\not<':u'≮', u'\\not=':u'≠', 
      u'\\not>':u'≯', u'\\not\\in':u' ∉ ', u'\\notbackslash':u'⍀', 
      u'\\notin':u'∉', u'\\notni':u'∌', u'\\notslash':u'⌿', 
      u'\\nparallel':u'∦', u'\\nprec':u'⊀', u'\\nrightarrow':u'↛', 
      u'\\nsim':u'≁', u'\\nsimeq':u'≄', u'\\nsqsubset':u'⊏̸', 
      u'\\nsubseteq':u'⊈', u'\\nsucc':u'⊁', u'\\nsucccurlyeq':u'⋡', 
      u'\\nsupset':u'⊅', u'\\nsupseteq':u'⊉', u'\\ntriangleleft':u'⋪', 
      u'\\ntrianglelefteq':u'⋬', u'\\ntriangleright':u'⋫', 
      u'\\ntrianglerighteq':u'⋭', u'\\nvDash':u'⊭', u'\\nvdash':u'⊬', 
      u'\\nwarrow':u'↖', u'\\odot':u'⊙', u'\\oiiint':u'∰', u'\\oiint':u'∯', 
      u'\\oint':u'∮', u'\\ointclockwise':u'∲', u'\\ointctrclockwise':u'∳', 
      u'\\ominus':u'⊖', u'\\oplus':u'⊕', u'\\oslash':u'⊘', u'\\otimes':u'⊗', 
      u'\\owns':u'∋', u'\\parallel':u'∥', u'\\partial':u'∂', u'\\perp':u'⊥', 
      u'\\pisces':u'♓', u'\\pitchfork':u'⋔', u'\\pluto':u'♇', u'\\pm':u'±', 
      u'\\pointer':u'➪', u'\\pounds':u'£', u'\\prec':u'≺', 
      u'\\preccurlyeq':u'≼', u'\\preceq':u'≼', u'\\precsim':u'≾', 
      u'\\prime':u'′', u'\\prod':u'<span class="bigsymbol">∏</span>', 
      u'\\prompto':u'∝', u'\\propto':u' ∝ ', u'\\qquad':u'  ', u'\\quad':u' ', 
      u'\\quarternote':u'♩', u'\\rangle':u'⟩', u'\\rbrace':u'}', 
      u'\\rbrace)':u'}', u'\\rbrack':u']', u'\\rceil':u'⌉', u'\\rfloor':u'⌋', 
      u'\\rhd':u'⊳', u'\\rightarrow':u' → ', u'\\rightarrow)':u'→', 
      u'\\rightarrowtail':u'↣', u'\\rightarrowtobar':u'⇥', 
      u'\\rightharpoondown':u'⇁', u'\\rightharpoonup':u'⇀', 
      u'\\rightharpooondown':u'⇁', u'\\rightharpooonup':u'⇀', 
      u'\\rightleftarrows':u'⇄', u'\\rightleftharpoons':u'⇌', 
      u'\\rightmoon':u'☽', u'\\rightrightarrows':u'⇉', 
      u'\\rightrightharpoons':u'⥤', u'\\rightsquigarrow':u' ⇝ ', 
      u'\\rightthreetimes':u'⋌', u'\\risingdotseq':u'≓', u'\\rtimes':u'⋊', 
      u'\\sagittarius':u'♐', u'\\saturn':u'♄', u'\\scorpio':u'♏', 
      u'\\scriptscriptstyle':u'', u'\\scriptstyle':u'', u'\\searrow':u'↘', 
      u'\\sec':u'sec', u'\\setminus':u'∖', u'\\sharp':u'♯', u'\\sim':u' ~ ', 
      u'\\simeq':u'≃', u'\\sin':u'sin', u'\\sinh':u'sinh', u'\\slash':u'∕', 
      u'\\smile':u'⌣', u'\\smiley':u'☺', u'\\spadesuit':u'♠', 
      u'\\sphericalangle':u'∢', u'\\sqcap':u'⊓', u'\\sqcup':u'⊔', 
      u'\\sqsubset':u'⊏', u'\\sqsubseteq':u'⊑', u'\\sqsupset':u'⊐', 
      u'\\sqsupseteq':u'⊒', u'\\square':u'□', u'\\star':u'⋆', 
      u'\\subset':u' ⊂ ', u'\\subseteq':u'⊆', u'\\subseteqq':u'⫅', 
      u'\\subsetneqq':u'⫋', u'\\succ':u'≻', u'\\succcurlyeq':u'≽', 
      u'\\succeq':u'≽', u'\\succnsim':u'⋩', u'\\succsim':u'≿', 
      u'\\sum':u'<span class="bigsymbol">∑</span>', u'\\sun':u'☼', 
      u'\\sup':u'sup', u'\\supset':u' ⊃ ', u'\\supseteq':u'⊇', 
      u'\\supseteqq':u'⫆', u'\\supsetneqq':u'⫌', u'\\surd':u'√', 
      u'\\swarrow':u'↙', u'\\tan':u'tan', u'\\tanh':u'tanh', u'\\taurus':u'♉', 
      u'\\textbackslash':u'\\', u'\\textstyle':u'', u'\\therefore':u'∴', 
      u'\\times':u' × ', u'\\to':u'→', u'\\top':u'⊤', u'\\triangle':u'△', 
      u'\\triangleleft':u'⊲', u'\\trianglelefteq':u'⊴', u'\\triangleq':u'≜', 
      u'\\triangleright':u'▷', u'\\trianglerighteq':u'⊵', 
      u'\\twoheadleftarrow':u'↞', u'\\twoheadrightarrow':u'↠', 
      u'\\twonotes':u'♫', u'\\udot':u'⊍', u'\\unlhd':u'⊴', u'\\unrhd':u'⊵', 
      u'\\unrhl':u'⊵', u'\\uparrow':u'↑', u'\\updownarrow':u'↕', 
      u'\\upharpoonleft':u'↿', u'\\upharpoonright':u'↾', u'\\uplus':u'⊎', 
      u'\\upuparrows':u'⇈', u'\\uranus':u'♅', u'\\vDash':u'⊨', 
      u'\\varclubsuit':u'♧', u'\\vardiamondsuit':u'♦', u'\\varheartsuit':u'♥', 
      u'\\varnothing':u'∅', u'\\varspadesuit':u'♤', u'\\vdash':u'⊢', 
      u'\\vdots':u'⋮', u'\\vee':u'∨', u'\\vee)':u'∨', u'\\veebar':u'⊻', 
      u'\\vert':u'∣', u'\\virgo':u'♍', u'\\wedge':u'∧', u'\\wedge)':u'∧', 
      u'\\wp':u'℘', u'\\wr':u'≀', u'\\yen':u'¥', u'\\{':u'{', u'\\|':u'∥', 
      u'\\}':u'}', 
      }

  decoratingfunctions = {
      u'\\acute':u'´', u'\\acute{A}':u'Á', u'\\acute{C}':u'Ć', 
      u'\\acute{E}':u'É', u'\\acute{G}':u'Ǵ', u'\\acute{I}':u'Í', 
      u'\\acute{K}':u'Ḱ', u'\\acute{L}':u'Ĺ', u'\\acute{M}':u'Ḿ', 
      u'\\acute{N}':u'Ń', u'\\acute{O}':u'Ó', u'\\acute{P}':u'Ṕ', 
      u'\\acute{R}':u'Ŕ', u'\\acute{S}':u'Ś', u'\\acute{U}':u'Ú', 
      u'\\acute{W}':u'Ẃ', u'\\acute{Y}':u'Ý', u'\\acute{Z}':u'Ź', 
      u'\\acute{a}':u'á', u'\\acute{c}':u'ć', u'\\acute{e}':u'é', 
      u'\\acute{g}':u'ǵ', u'\\acute{i}':u'í', u'\\acute{k}':u'ḱ', 
      u'\\acute{l}':u'ĺ', u'\\acute{m}':u'ḿ', u'\\acute{n}':u'ń', 
      u'\\acute{o}':u'ó', u'\\acute{p}':u'ṕ', u'\\acute{r}':u'ŕ', 
      u'\\acute{s}':u'ś', u'\\acute{u}':u'ú', u'\\acute{w}':u'ẃ', 
      u'\\acute{y}':u'ý', u'\\acute{z}':u'ź', u'\\bar{A}':u'Ā', 
      u'\\bar{E}':u'Ē', u'\\bar{I}':u'Ī', u'\\bar{O}':u'Ō', u'\\bar{U}':u'Ū', 
      u'\\bar{Y}':u'Ȳ', u'\\bar{a}':u'ā', u'\\bar{e}':u'ē', u'\\bar{o}':u'ō', 
      u'\\bar{u}':u'ū', u'\\bar{y}':u'ȳ', u'\\breve':u'˘', u'\\breve{A}':u'Ă', 
      u'\\breve{E}':u'Ĕ', u'\\breve{G}':u'Ğ', u'\\breve{I}':u'Ĭ', 
      u'\\breve{O}':u'Ŏ', u'\\breve{U}':u'Ŭ', u'\\breve{a}':u'ă', 
      u'\\breve{e}':u'ĕ', u'\\breve{g}':u'ğ', u'\\breve{o}':u'ŏ', 
      u'\\breve{u}':u'ŭ', u'\\c':u'¸', u'\\check':u'ˇ', u'\\check{A}':u'Ǎ', 
      u'\\check{C}':u'Č', u'\\check{D}':u'Ď', u'\\check{E}':u'Ě', 
      u'\\check{G}':u'Ǧ', u'\\check{H}':u'Ȟ', u'\\check{I}':u'Ǐ', 
      u'\\check{K}':u'Ǩ', u'\\check{N}':u'Ň', u'\\check{O}':u'Ǒ', 
      u'\\check{R}':u'Ř', u'\\check{S}':u'Š', u'\\check{T}':u'Ť', 
      u'\\check{U}':u'Ǔ', u'\\check{Z}':u'Ž', u'\\check{a}':u'ǎ', 
      u'\\check{c}':u'č', u'\\check{d}':u'ď', u'\\check{e}':u'ě', 
      u'\\check{g}':u'ǧ', u'\\check{h}':u'ȟ', u'\\check{k}':u'ǩ', 
      u'\\check{n}':u'ň', u'\\check{o}':u'ǒ', u'\\check{r}':u'ř', 
      u'\\check{s}':u'š', u'\\check{u}':u'ǔ', u'\\check{z}':u'ž', 
      u'\\c{C}':u'Ç', u'\\c{D}':u'Ḑ', u'\\c{E}':u'Ȩ', u'\\c{G}':u'Ģ', 
      u'\\c{H}':u'Ḩ', u'\\c{K}':u'Ķ', u'\\c{L}':u'Ļ', u'\\c{N}':u'Ņ', 
      u'\\c{R}':u'Ŗ', u'\\c{S}':u'Ş', u'\\c{T}':u'Ţ', u'\\c{c}':u'ç', 
      u'\\c{d}':u'ḑ', u'\\c{e}':u'ȩ', u'\\c{h}':u'ḩ', u'\\c{k}':u'ķ', 
      u'\\c{l}':u'ļ', u'\\c{n}':u'ņ', u'\\c{r}':u'ŗ', u'\\c{s}':u'ş', 
      u'\\c{t}':u'ţ', u'\\dacute{O}':u'Ő', u'\\dacute{U}':u'Ű', 
      u'\\dacute{o}':u'ő', u'\\dacute{u}':u'ű', u'\\ddot':u'¨', 
      u'\\ddot{A}':u'Ä', u'\\ddot{E}':u'Ë', u'\\ddot{H}':u'Ḧ', 
      u'\\ddot{I}':u'Ï', u'\\ddot{O}':u'Ö', u'\\ddot{U}':u'Ü', 
      u'\\ddot{W}':u'Ẅ', u'\\ddot{X}':u'Ẍ', u'\\ddot{Y}':u'Ÿ', 
      u'\\ddot{a}':u'ä', u'\\ddot{e}':u'ë', u'\\ddot{h}':u'ḧ', 
      u'\\ddot{o}':u'ö', u'\\ddot{t}':u'ẗ', u'\\ddot{u}':u'ü', 
      u'\\ddot{w}':u'ẅ', u'\\ddot{x}':u'ẍ', u'\\ddot{y}':u'ÿ', 
      u'\\dgrave{A}':u'Ȁ', u'\\dgrave{E}':u'Ȅ', u'\\dgrave{I}':u'Ȉ', 
      u'\\dgrave{O}':u'Ȍ', u'\\dgrave{R}':u'Ȑ', u'\\dgrave{U}':u'Ȕ', 
      u'\\dgrave{a}':u'ȁ', u'\\dgrave{e}':u'ȅ', u'\\dgrave{o}':u'ȍ', 
      u'\\dgrave{r}':u'ȑ', u'\\dgrave{u}':u'ȕ', u'\\dot':u'˙', 
      u'\\dot{A}':u'Ȧ', u'\\dot{B}':u'Ḃ', u'\\dot{C}':u'Ċ', u'\\dot{D}':u'Ḋ', 
      u'\\dot{E}':u'Ė', u'\\dot{F}':u'Ḟ', u'\\dot{G}':u'Ġ', u'\\dot{H}':u'Ḣ', 
      u'\\dot{I}':u'İ', u'\\dot{M}':u'Ṁ', u'\\dot{N}':u'Ṅ', u'\\dot{O}':u'Ȯ', 
      u'\\dot{P}':u'Ṗ', u'\\dot{R}':u'Ṙ', u'\\dot{S}':u'Ṡ', u'\\dot{T}':u'Ṫ', 
      u'\\dot{W}':u'Ẇ', u'\\dot{X}':u'Ẋ', u'\\dot{Y}':u'Ẏ', u'\\dot{Z}':u'Ż', 
      u'\\dot{a}':u'ȧ', u'\\dot{b}':u'ḃ', u'\\dot{c}':u'ċ', u'\\dot{d}':u'ḋ', 
      u'\\dot{e}':u'ė', u'\\dot{f}':u'ḟ', u'\\dot{g}':u'ġ', u'\\dot{h}':u'ḣ', 
      u'\\dot{m}':u'ṁ', u'\\dot{n}':u'ṅ', u'\\dot{o}':u'ȯ', u'\\dot{p}':u'ṗ', 
      u'\\dot{r}':u'ṙ', u'\\dot{s}':u'ṡ', u'\\dot{t}':u'ṫ', u'\\dot{w}':u'ẇ', 
      u'\\dot{x}':u'ẋ', u'\\dot{y}':u'ẏ', u'\\dot{z}':u'ż', u'\\grave':u'`', 
      u'\\grave{A}':u'À', u'\\grave{E}':u'È', u'\\grave{I}':u'Ì', 
      u'\\grave{N}':u'Ǹ', u'\\grave{O}':u'Ò', u'\\grave{U}':u'Ù', 
      u'\\grave{W}':u'Ẁ', u'\\grave{Y}':u'Ỳ', u'\\grave{a}':u'à', 
      u'\\grave{e}':u'è', u'\\grave{n}':u'ǹ', u'\\grave{o}':u'ò', 
      u'\\grave{u}':u'ù', u'\\grave{w}':u'ẁ', u'\\grave{y}':u'ỳ', 
      u'\\hat':u'^', u'\\hat{A}':u'Â', u'\\hat{C}':u'Ĉ', u'\\hat{E}':u'Ê', 
      u'\\hat{G}':u'Ĝ', u'\\hat{H}':u'Ĥ', u'\\hat{I}':u'Î', u'\\hat{J}':u'Ĵ', 
      u'\\hat{O}':u'Ô', u'\\hat{S}':u'Ŝ', u'\\hat{U}':u'Û', u'\\hat{W}':u'Ŵ', 
      u'\\hat{Y}':u'Ŷ', u'\\hat{Z}':u'Ẑ', u'\\hat{a}':u'â', u'\\hat{c}':u'ĉ', 
      u'\\hat{e}':u'ê', u'\\hat{g}':u'ĝ', u'\\hat{h}':u'ĥ', u'\\hat{o}':u'ô', 
      u'\\hat{s}':u'ŝ', u'\\hat{u}':u'û', u'\\hat{w}':u'ŵ', u'\\hat{y}':u'ŷ', 
      u'\\hat{z}':u'ẑ', u'\\mathring':u'°', u'\\ogonek{A}':u'Ą', 
      u'\\ogonek{E}':u'Ę', u'\\ogonek{I}':u'Į', u'\\ogonek{O}':u'Ǫ', 
      u'\\ogonek{U}':u'Ų', u'\\ogonek{a}':u'ą', u'\\ogonek{e}':u'ę', 
      u'\\ogonek{i}':u'į', u'\\ogonek{o}':u'ǫ', u'\\ogonek{u}':u'ų', 
      u'\\overleftarrow':u'⟵', u'\\overrightarrow':u'⟶', u'\\rcap{A}':u'Ȃ', 
      u'\\rcap{E}':u'Ȇ', u'\\rcap{I}':u'Ȋ', u'\\rcap{O}':u'Ȏ', 
      u'\\rcap{R}':u'Ȓ', u'\\rcap{U}':u'Ȗ', u'\\rcap{a}':u'ȃ', 
      u'\\rcap{e}':u'ȇ', u'\\rcap{o}':u'ȏ', u'\\rcap{r}':u'ȓ', 
      u'\\rcap{u}':u'ȗ', u'\\slashed{O}':u'Ø', u'\\slashed{o}':u'ø', 
      u'\\subdot{A}':u'Ạ', u'\\subdot{B}':u'Ḅ', u'\\subdot{D}':u'Ḍ', 
      u'\\subdot{E}':u'Ẹ', u'\\subdot{H}':u'Ḥ', u'\\subdot{I}':u'Ị', 
      u'\\subdot{K}':u'Ḳ', u'\\subdot{L}':u'Ḷ', u'\\subdot{M}':u'Ṃ', 
      u'\\subdot{N}':u'Ṇ', u'\\subdot{O}':u'Ọ', u'\\subdot{R}':u'Ṛ', 
      u'\\subdot{S}':u'Ṣ', u'\\subdot{T}':u'Ṭ', u'\\subdot{U}':u'Ụ', 
      u'\\subdot{V}':u'Ṿ', u'\\subdot{W}':u'Ẉ', u'\\subdot{Y}':u'Ỵ', 
      u'\\subdot{Z}':u'Ẓ', u'\\subdot{a}':u'ạ', u'\\subdot{b}':u'ḅ', 
      u'\\subdot{d}':u'ḍ', u'\\subdot{e}':u'ẹ', u'\\subdot{h}':u'ḥ', 
      u'\\subdot{i}':u'ị', u'\\subdot{k}':u'ḳ', u'\\subdot{l}':u'ḷ', 
      u'\\subdot{m}':u'ṃ', u'\\subdot{n}':u'ṇ', u'\\subdot{o}':u'ọ', 
      u'\\subdot{r}':u'ṛ', u'\\subdot{s}':u'ṣ', u'\\subdot{t}':u'ṭ', 
      u'\\subdot{u}':u'ụ', u'\\subdot{v}':u'ṿ', u'\\subdot{w}':u'ẉ', 
      u'\\subdot{y}':u'ỵ', u'\\subdot{z}':u'ẓ', u'\\subhat{D}':u'Ḓ', 
      u'\\subhat{E}':u'Ḙ', u'\\subhat{L}':u'Ḽ', u'\\subhat{N}':u'Ṋ', 
      u'\\subhat{T}':u'Ṱ', u'\\subhat{U}':u'Ṷ', u'\\subhat{d}':u'ḓ', 
      u'\\subhat{e}':u'ḙ', u'\\subhat{l}':u'ḽ', u'\\subhat{n}':u'ṋ', 
      u'\\subhat{t}':u'ṱ', u'\\subhat{u}':u'ṷ', u'\\subring{A}':u'Ḁ', 
      u'\\subring{a}':u'ḁ', u'\\subtilde{E}':u'Ḛ', u'\\subtilde{I}':u'Ḭ', 
      u'\\subtilde{U}':u'Ṵ', u'\\subtilde{e}':u'ḛ', u'\\subtilde{i}':u'ḭ', 
      u'\\subtilde{u}':u'ṵ', u'\\tilde':u'˜', u'\\tilde{A}':u'Ã', 
      u'\\tilde{E}':u'Ẽ', u'\\tilde{I}':u'Ĩ', u'\\tilde{N}':u'Ñ', 
      u'\\tilde{O}':u'Õ', u'\\tilde{U}':u'Ũ', u'\\tilde{V}':u'Ṽ', 
      u'\\tilde{Y}':u'Ỹ', u'\\tilde{a}':u'ã', u'\\tilde{e}':u'ẽ', 
      u'\\tilde{n}':u'ñ', u'\\tilde{o}':u'õ', u'\\tilde{u}':u'ũ', 
      u'\\tilde{v}':u'ṽ', u'\\tilde{y}':u'ỹ', u'\\vec':u'→', 
      }

  definingfunctions = {
      u'\\newcommand':[u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}',u'',], 
      u'\\renewcommand':[u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}',u'',], 
      }

  endings = {
      u'bracket':u'}', u'complex':u'\\]', u'endafter':u'}', 
      u'endbefore':u'\\end{', u'squarebracket':u']', 
      }

  environments = {
      u'align':[u'r',u'l',], u'eqnarray':[u'r',u'c',u'l',], 
      u'gathered':[u'l',u'l',], 
      }

  fontfunctions = {
      u'\\boldsymbol':u'b', u'\\mathbb':u'span class="blackboard"', 
      u'\\mathbb{A}':u'𝔸', u'\\mathbb{B}':u'𝔹', u'\\mathbb{C}':u'ℂ', 
      u'\\mathbb{D}':u'𝔻', u'\\mathbb{E}':u'𝔼', u'\\mathbb{F}':u'𝔽', 
      u'\\mathbb{G}':u'𝔾', u'\\mathbb{H}':u'ℍ', u'\\mathbb{J}':u'𝕁', 
      u'\\mathbb{K}':u'𝕂', u'\\mathbb{L}':u'𝕃', u'\\mathbb{N}':u'ℕ', 
      u'\\mathbb{O}':u'𝕆', u'\\mathbb{P}':u'ℙ', u'\\mathbb{Q}':u'ℚ', 
      u'\\mathbb{R}':u'ℝ', u'\\mathbb{S}':u'𝕊', u'\\mathbb{T}':u'𝕋', 
      u'\\mathbb{W}':u'𝕎', u'\\mathbb{Z}':u'ℤ', u'\\mathbf':u'b', 
      u'\\mathcal':u'span class="script"', 
      u'\\mathfrak':u'span class="fraktur"', u'\\mathfrak{C}':u'ℭ', 
      u'\\mathfrak{F}':u'𝔉', u'\\mathfrak{H}':u'ℌ', u'\\mathfrak{I}':u'ℑ', 
      u'\\mathfrak{R}':u'ℜ', u'\\mathfrak{Z}':u'ℨ', u'\\mathit':u'i', 
      u'\\mathring{A}':u'Å', u'\\mathring{U}':u'Ů', u'\\mathring{a}':u'å', 
      u'\\mathring{u}':u'ů', u'\\mathring{w}':u'ẘ', u'\\mathring{y}':u'ẙ', 
      u'\\mathrm':u'span class="mathrm"', u'\\mathscr':u'span class="script"', 
      u'\\mathscr{B}':u'ℬ', u'\\mathscr{E}':u'ℰ', u'\\mathscr{F}':u'ℱ', 
      u'\\mathscr{H}':u'ℋ', u'\\mathscr{I}':u'ℐ', u'\\mathscr{L}':u'ℒ', 
      u'\\mathscr{M}':u'ℳ', u'\\mathscr{R}':u'ℛ', 
      u'\\mathsf':u'span class="mathsf"', u'\\mathtt':u'tt', 
      }

  hybridfunctions = {
      
      u'\\binom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="binom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\cfrac':[u'[$p!]{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fullfraction"',u'span class="numerator$p"',u'span class="denominator"',], 
      u'\\dbinom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="fullbinom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\dfrac':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fullfraction"',u'span class="numerator"',u'span class="denominator"',], 
      u'\\frac':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="fraction"',u'span class="numerator"',u'span class="denominator"',], 
      u'\\hspace':[u'{$p!}',u'f0{ }',u'span class="hspace" style="width: $p;"',], 
      u'\\leftroot':[u'{$p!}',u'f0{ }',u'span class="leftroot" style="width: $p;px"',], 
      u'\\nicefrac':[u'{$1}{$2}',u'f0{f1{$1}⁄f2{$2}}',u'span class="fraction"',u'sup class="numerator"',u'sub class="denominator"',], 
      u'\\raisebox':[u'{$p!}{$1}',u'f0{$1}',u'span class="raisebox" style="vertical-align: $p;"',], 
      u'\\renewenvironment':[u'{$1!}{$2!}{$3!}',u'',], 
      u'\\sqrt':[u'[$0]{$1}',u'f1{$0}f0{f2{√}f3{$1}}',u'span class="sqrt"',u'sup',u'span class="radical"',u'span class="root"',], 
      u'\\tbinom':[u'{$1}{$2}',u'f3{(}f0{f1{$1}f2{$2}}f3{)}',u'span class="fullbinom"',u'span class="upbinom"',u'span class="downbinom"',u'span class="bigsymbol"',], 
      u'\\unit':[u'[$0]{$1}',u'$0f0{$1.font}',u'span class="unit"',], 
      u'\\unitfrac':[u'[$0]{$1}{$2}',u'$0f0{f1{$1.font}⁄f2{$2.font}}',u'span class="fraction"',u'sup class="unit"',u'sub class="unit"',], 
      u'\\uproot':[u'{$p!}',u'f0{ }',u'span class="uproot" style="width: $p;px"',], 
      u'\\vspace':[u'{$p!}',u'f0{ }',u'span class="vspace" style="height: $p;"',], 
      }

  labelfunctions = {
      u'\\label':u'a name="#"', 
      }

  limits = {
      u'commands':[u'\\sum',u'\\int',u'\\intop',], u'operands':[u'^',u'_',], 
      }

  modified = {
      u'\n':u'', u' ':u'', u'$':u'', u'&':u'	', u'\'':u'’', u'+':u' + ', 
      u',':u', ', u'-':u' − ', u'/':u' ⁄ ', u'<':u' &lt; ', u'=':u' = ', 
      u'>':u' &gt; ', u'@':u'', u'~':u'', 
      }

  onefunctions = {
      u'\\Big':u'span class="bigsymbol"', u'\\Bigg':u'span class="hugesymbol"', 
      u'\\bar':u'span class="bar"', u'\\begin{array}':u'span class="arraydef"', 
      u'\\big':u'span class="symbol"', u'\\bigg':u'span class="largesymbol"', 
      u'\\bigl':u'span class="bigsymbol"', u'\\bigr':u'span class="bigsymbol"', 
      u'\\ensuremath':u'span class="ensuremath"', 
      u'\\hphantom':u'span class="phantom"', u'\\left':u'span class="symbol"', 
      u'\\left.':u'<span class="leftdot"></span>', 
      u'\\middle':u'span class="symbol"', 
      u'\\overbrace':u'span class="overbrace"', 
      u'\\overline':u'span class="overline"', 
      u'\\phantom':u'span class="phantom"', u'\\right':u'span class="symbol"', 
      u'\\right.':u'<span class="rightdot"></span>', 
      u'\\underbrace':u'span class="underbrace"', u'\\underline':u'u', 
      u'\\vphantom':u'span class="phantom"', 
      }

  starts = {
      u'beginafter':u'}', u'beginbefore':u'\\begin{', u'bracket':u'{', 
      u'command':u'\\', u'complex':u'\\[', u'simple':u'$', 
      u'squarebracket':u'[', u'unnumbered':u'*', 
      }

  symbolfunctions = {
      u'^':u'sup', u'_':u'sub', 
      }

  textfunctions = {
      u'\\mbox':u'span class="mbox"', u'\\text':u'span class="text"', 
      u'\\textbf':u'b', u'\\textipa':u'span class="textipa"', u'\\textit':u'i', 
      u'\\textrm':u'span class="mathrm"', 
      u'\\textsc':u'span class="versalitas"', 
      u'\\textsf':u'span class="mathsf"', u'\\textsl':u'i', u'\\texttt':u'tt', 
      u'\\textup':u'span class="normal"', 
      }

  underdecoratingfunctions = {
      u'\\r':u'∘', u'\\s':u'ˌ', u'\\textsubring':u'∘', 
      }

  unmodified = {
      
      u'characters':[u'.',u'*',u'€',u'(',u')',u'[',u']',u':',u'·',u'!',u';',u'|',u'§',u'"',], 
      }

class GeneralConfig(object):
  "Configuration class from config file"

  version = {
      u'date':u'2010-05-13', u'lyxformat':u'345', u'number':u'0.98', 
      }

class HeaderConfig(object):
  "Configuration class from config file"

  parameters = {
      u'beginpreamble':u'\\begin_preamble', u'branch':u'\\branch', 
      u'documentclass':u'\\textclass', u'endbranch':u'\\end_branch', 
      u'endpreamble':u'\\end_preamble', u'language':u'\\language', 
      u'lstset':u'\\lstset', u'paragraphseparation':u'\\paragraph_separation', 
      u'pdftitle':u'\\pdf_title', u'secnumdepth':u'\\secnumdepth', 
      u'tocdepth':u'\\tocdepth', 
      }

  styles = {
      
      u'article':[u'article',u'aastex',u'aapaper',u'acmsiggraph',u'sigplanconf',u'achemso',u'amsart',u'apa',u'arab-article',u'armenian-article',u'article-beamer',u'chess',u'dtk',u'elsarticle',u'heb-article',u'IEEEtran',u'iopart',u'kluwer',u'scrarticle-beamer',u'scrartcl',u'extarticle',u'paper',u'mwart',u'revtex4',u'spie',u'svglobal3',u'ltugboat',u'agu-dtd',u'jgrga',u'agums',u'entcs',u'egs',u'ijmpc',u'ijmpd',u'singlecol-new',u'doublecol-new',u'isprs',u'tarticle',u'jsarticle',u'jarticle',u'jss',u'literate-article',u'siamltex',u'cl2emult',u'llncs',u'svglobal',u'svjog',u'svprobth',], 
      }

class ImageConfig(object):
  "Configuration class from config file"

  converters = {
      
      u'imagemagick':u'convert [-density $scale] [-pepito $juanito] [-tonto $decapi] -define pdf:use-cropbox=true "$input" "$output"', 
      u'inkscape':u'inkscape "$input" --export-png="$output"', 
      }

  formats = {
      u'default':u'.png', u'raster':[u'.png',u'.jpg',], 
      u'vector':[u'.svg',u'.eps',], 
      }

  size = {
      u'ignoredtexts':[u'col',u'text',u'line',u'page',u'theight',u'pheight',], 
      }

class NewfangleConfig(object):
  "Configuration class from config file"

  constants = {
      u'chunkref':u'chunkref{', u'endcommand':u'}', u'endmark':u'&gt;', 
      u'startcommand':u'\\', u'startmark':u'=&lt;', 
      }

class NumberingConfig(object):
  "Configuration class from config file"

  layouts = {
      
      u'ordered':[u'Chapter',u'Section',u'Subsection',u'Subsubsection',u'Paragraph',], 
      u'unique':[u'Part',u'Book',], 
      }

class StyleConfig(object):
  "Configuration class from config file"

  quotes = {
      u'ald':u'»', u'als':u'›', u'ard':u'«', u'ars':u'‹', u'eld':u'“', 
      u'els':u'‘', u'erd':u'”', u'ers':u'’', u'fld':u'«', u'fls':u'‹', 
      u'frd':u'»', u'frs':u'›', u'gld':u'„', u'gls':u'‚', u'grd':u'“', 
      u'grs':u'‘', u'pld':u'„', u'pls':u'‚', u'prd':u'”', u'prs':u'’', 
      u'sld':u'”', u'srd':u'”', 
      }

  spaces = {
      u'\\enskip{}':u' ', u'\\hfill{}':u'<span class="hfill"> </span>', 
      u'\\hspace*{\\fill}':u' ', u'\\hspace*{}':u'', u'\\hspace{}':u' ', 
      u'\\negthinspace{}':u'', u'\\qquad{}':u'  ', u'\\quad{}':u' ', 
      u'\\space{}':u' ', u'\\thinspace{}':u' ', u'~':u' ', 
      }

class TagConfig(object):
  "Configuration class from config file"

  barred = {
      u'under':u'u', 
      }

  family = {
      u'sans':u'span class="sans"', u'typewriter':u'tt', 
      }

  flex = {
      u'CharStyle:Code':u'span class="code"', 
      u'CharStyle:MenuItem':u'span class="menuitem"', 
      }

  layouts = {
      u'Center':u'div', u'Chapter':u'h?', u'Date':u'h2', u'Paragraph':u'div', 
      u'Part':u'h1', u'Quotation':u'blockquote', u'Quote':u'blockquote', 
      u'Section':u'h?', u'Subsection':u'h?', u'Subsubsection':u'h?', 
      }

  listitems = {
      u'Enumerate':u'ol', u'Itemize':u'ul', 
      }

  notes = {
      u'Comment':u'', u'Greyedout':u'span class="greyedout"', u'Note':u'', 
      }

  shaped = {
      u'italic':u'i', u'slanted':u'i', u'smallcaps':u'span class="versalitas"', 
      }

class TranslationConfig(object):
  "Configuration class from config file"

  constants = {
      u'Book':u'Book', u'Chapter':u'Chapter', u'Paragraph':u'Paragraph', 
      u'Part':u'Part', u'Section':u'Section', u'Subsection':u'Subsection', 
      u'Subsubsection':u'Subsubsection', u'abstract':u'Abstract', 
      u'bibliography':u'Bibliography', u'figure':u'figure', 
      u'float-algorithm':u'Algorithm ', u'float-figure':u'Figure ', 
      u'float-listing':u'Listing ', u'float-table':u'Table ', 
      u'float-tableau':u'Tableau ', u'index':u'Index', 
      u'jsmath-enable':u'Please enable JavaScript on your browser.', 
      u'jsmath-requires':u' requires JavaScript to correctly process the mathematics on this page. ', 
      u'jsmath-warning':u'Warning: ', u'list-algorithm':u'List of Algorithms', 
      u'list-figure':u'List of Figures', u'list-table':u'List of Tables', 
      u'list-tableau':u'List of Tableaux', u'next':u'Next', 
      u'nomenclature':u'Nomenclature', u'on-page':u' on page ', 
      u'prev':u'Previous', u'toc':u'Table of Contents', u'up':u'Up', 
      }

  languages = {
      u'deutsch':u'de', u'dutch':u'nl', u'english':u'en', u'french':u'fr', 
      u'ngerman':u'de', u'spanish':u'es', 
      }



class CommandLineParser(object):
  "A parser for runtime options"

  def __init__(self, options):
    self.options = options

  def parseoptions(self, args):
    "Parse command line options"
    if len(args) == 0:
      return None
    while len(args) > 0 and args[0].startswith('--'):
      key, value = self.readoption(args)
      if not key:
        return 'Option ' + value + ' not recognized'
      if not value:
        return 'Option ' + key + ' needs a value'
      setattr(self.options, key, value)
    return None

  def readoption(self, args):
    "Read the key and value for an option"
    arg = args[0][2:]
    del args[0]
    if '=' in arg:
      return self.readequals(arg, args)
    key = arg
    if not hasattr(self.options, key):
      return None, key
    current = getattr(self.options, key)
    if current.__class__ == bool:
      return key, True
    # read value
    if len(args) == 0:
      return key, None
    if args[0].startswith('"'):
      initial = args[0]
      del args[0]
      return key, self.readquoted(args, initial)
    value = args[0]
    del args[0]
    return key, value

  def readquoted(self, args, initial):
    "Read a value between quotes"
    value = initial[1:]
    while len(args) > 0 and not args[0].endswith('"') and not args[0].startswith('--'):
      value += ' ' + args[0]
      del args[0]
    if len(args) == 0 or args[0].startswith('--'):
      return None
    value += ' ' + args[0:-1]
    return value

  def readequals(self, arg, args):
    "Read a value with equals"
    split = arg.split('=', 1)
    key = split[0]
    value = split[1]
    if not value.startswith('"'):
      return key, value
    return key, self.readquoted(args, value)



class Options(object):
  "A set of runtime options"

  instance = None

  location = None
  nocopy = False
  debug = False
  quiet = False
  version = False
  hardversion = False
  versiondate = False
  html = False
  help = False
  showlines = True
  unicode = False
  iso885915 = False
  css = 'css/lyx.css'
  title = None
  directory = None
  destdirectory = None
  toc = False
  toctarget = ''
  forceformat = None
  lyxformat = False
  target = None
  splitpart = None
  memory = True
  lowmem = False
  nobib = False
  converter = 'imagemagick'
  numberfoot = False
  raw = False
  jsmath = None
  mathjax = None
  nofooter = None

  branches = dict()

  def parseoptions(self, args):
    "Parse command line options"
    Options.location = args[0]
    del args[0]
    parser = CommandLineParser(Options)
    result = parser.parseoptions(args)
    if result:
      Trace.error(result)
      self.usage()
    if Options.help:
      self.usage()
    if Options.version:
      self.showversion()
    if Options.hardversion:
      self.showhardversion()
    if Options.versiondate:
      self.showversiondate()
    if Options.lyxformat:
      self.showlyxformat()
    if Options.splitpart:
      try:
        Options.splitpart = int(Options.splitpart)
        if Options.splitpart <= 0:
          Trace.error('--splitpart requires a number bigger than zero')
          self.usage()
      except:
        Trace.error('--splitpart needs a numeric argument, not ' + Options.splitpart)
        self.usage()
    if Options.lowmem or Options.toc:
      Options.memory = False
    # set in Trace if necessary
    for param in dir(Options):
      if hasattr(Trace, param + 'mode'):
        setattr(Trace, param + 'mode', getattr(self, param))

  def usage(self):
    "Show correct usage"
    Trace.error('Usage: ' + os.path.basename(Options.location) + ' [options] [filein] [fileout]')
    Trace.error('Convert LyX input file "filein" to HTML file "fileout".')
    Trace.error('If filein (or fileout) is not given use standard input (or output).')
    Trace.error('Main program of the eLyXer package (http://elyxer.nongnu.org/).')
    self.showoptions()

  def showoptions(self):
    "Show all possible options"
    Trace.error('  Common options:')
    Trace.error('    --nocopy:               disables the copyright notice at the bottom')
    Trace.error('    --quiet:                disables all runtime messages')
    Trace.error('    --debug:                enable debugging messages (for developers)')
    Trace.error('    --title "title":        set the generated page title')
    Trace.error('    --directory "img_dir":  look for images in the specified directory')
    Trace.error('    --destdirectory "dest": put converted images into this directory')
    Trace.error('    --css "file.css":       use a custom CSS file')
    Trace.error('    --html:                 output HTML 4.0 instead of the default XHTML')
    Trace.error('    --unicode:              full Unicode output')
    Trace.error('    --iso885915:            output a document with ISO-8859-15 encoding')
    Trace.error('')
    Trace.error('  Esoteric options:')
    Trace.error('    --version:              show version number and release date')
    Trace.error('    --nofooter:             remove the footer "create by eLyXer"')
    Trace.error('    --forceformat ".ext":   force image output format')
    Trace.error('    --lyxformat:            return the highest LyX version supported')
    Trace.error('    --toc:                  create a table of contents')
    Trace.error('    --target "frame":       make all links point to the given frame')
    Trace.error('    --lowmem:               do the conversion on the fly (conserve memory)')
    Trace.error('    --converter inkscape:   use Inkscape to convert images')
    Trace.error('    --numberfoot:           label footnotes with numbers instead of letters')
    Trace.error('    --raw:                  generate HTML without header or footer.')
    Trace.error('    --jsmath "URL":         use jsMath from the given URL to display equations')
    Trace.error('    --mathjax "URL":        use MathJax from the given URL to display equations')
    exit()

  def showversion(self):
    "Return the current eLyXer version string"
    string = 'eLyXer version ' + GeneralConfig.version['number']
    string += ' (' + GeneralConfig.version['date'] + ')'
    Trace.error(string)
    exit()

  def showhardversion(self):
    "Return just the version string"
    Trace.message(GeneralConfig.version['number'])
    exit()

  def showversiondate(self):
    "Return just the version dte"
    Trace.message(GeneralConfig.version['date'])
    exit()

  def showlyxformat(self):
    "Return just the lyxformat parameter"
    Trace.message(GeneralConfig.version['lyxformat'])
    exit()

class BranchOptions(object):
  "A set of options for a branch"

  def __init__(self, name):
    self.name = name
    self.options = {'color':'#ffffff'}

  def set(self, key, value):
    "Set a branch option"
    if not key.startswith(ContainerConfig.string['startcommand']):
      Trace.error('Invalid branch option ' + key)
      return
    key = key.replace(ContainerConfig.string['startcommand'], '')
    self.options[key] = value

  def isselected(self):
    "Return if the branch is selected"
    if not 'selected' in self.options:
      return False
    return self.options['selected'] == '1'

  def __unicode__(self):
    "String representation"
    return 'options for ' + self.name + ': ' + unicode(self.options)







import codecs


class Parser(object):
  "A generic parser"

  def __init__(self):
    self.begin = 0
    self.parameters = dict()

  def parseheader(self, reader):
    "Parse the header"
    header = reader.currentline().split()
    reader.nextline()
    self.begin = reader.linenumber
    return header

  def parseparameter(self, reader):
    "Parse a parameter"
    if reader.currentline().strip().startswith('<'):
      key, value = self.parsexml(reader)
      self.parameters[key] = value
      return
    split = reader.currentline().strip().split(' ', 1)
    reader.nextline()
    if len(split) == 0:
      return
    key = split[0]
    if len(split) == 1:
      self.parameters[key] = True
      return
    if not '"' in split[1]:
      self.parameters[key] = split[1].strip()
      return
    doublesplit = split[1].split('"')
    self.parameters[key] = doublesplit[1]

  def parsexml(self, reader):
    "Parse a parameter in xml form: <param attr1=value...>"
    strip = reader.currentline().strip()
    reader.nextline()
    if not strip.endswith('>'):
      Trace.error('XML parameter ' + strip + ' should be <...>')
    split = strip[1:-1].split()
    if len(split) == 0:
      Trace.error('Empty XML parameter <>')
      return None, None
    key = split[0]
    del split[0]
    if len(split) == 0:
      return key, dict()
    attrs = dict()
    for attr in split:
      if not '=' in attr:
        Trace.error('Erroneous attribute ' + attr)
        attr += '="0"'
      parts = attr.split('=')
      attrkey = parts[0]
      value = parts[1].split('"')[1]
      attrs[attrkey] = value
    return key, attrs

  def parseending(self, reader, process):
    "Parse until the current ending is found"
    while not reader.currentline().startswith(self.ending):
      process()

  def parsecontainer(self, reader, contents):
    container = self.factory.createcontainer(reader)
    if container:
      container.parent = self.parent
      contents.append(container)

  def __unicode__(self):
    "Return a description"
    return self.__class__.__name__ + ' (' + unicode(self.begin) + ')'

class LoneCommand(Parser):
  "A parser for just one command line"

  def parse(self,reader):
    "Read nothing"
    return []

class TextParser(Parser):
  "A parser for a command and a bit of text"

  stack = []

  def __init__(self, ending):
    Parser.__init__(self)
    self.ending = ending
    self.endings = []

  def parse(self, reader):
    "Parse lines as long as they are text"
    TextParser.stack.append(self.ending)
    self.endings = TextParser.stack + [ContainerConfig.endings['Layout'],
        ContainerConfig.endings['Inset'], self.ending]
    contents = []
    while not self.isending(reader):
      self.parsecontainer(reader, contents)
    return contents

  def isending(self, reader):
    "Check if text is ending"
    current = reader.currentline().split()
    if len(current) == 0:
      return False
    if current[0] in self.endings:
      if current[0] in TextParser.stack:
        TextParser.stack.remove(current[0])
      else:
        TextParser.stack = []
      return True
    return False

class ExcludingParser(Parser):
  "A parser that excludes the final line"

  def parse(self, reader):
    "Parse everything up to (and excluding) the final line"
    contents = []
    self.parseending(reader, lambda: self.parsecontainer(reader, contents))
    return contents

class BoundedParser(ExcludingParser):
  "A parser bound by a final line"

  def parse(self, reader):
    "Parse everything, including the final line"
    contents = ExcludingParser.parse(self, reader)
    # skip last line
    reader.nextline()
    return contents

class BoundedDummy(Parser):
  "A bound parser that ignores everything"

  def parse(self, reader):
    "Parse the contents of the container"
    self.parseending(reader, lambda: reader.nextline())
    # skip last line
    reader.nextline()
    return []

class StringParser(Parser):
  "Parses just a string"

  def parseheader(self, reader):
    "Do nothing, just take note"
    self.begin = reader.linenumber + 1
    return []

  def parse(self, reader):
    "Parse a single line"
    contents = [reader.currentline()]
    reader.nextline()
    return contents

class InsetParser(BoundedParser):
  "Parses a LyX inset"

  def parse(self, reader):
    "Parse inset parameters into a dictionary"
    startcommand = ContainerConfig.string['startcommand']
    while reader.currentline() != '' and not reader.currentline().startswith(startcommand):
      self.parseparameter(reader)
    return BoundedParser.parse(self, reader)




import codecs
import datetime


class EmptyOutput(object):
  "The output for some container"

  def gethtml(self, container):
    "Return empty HTML code"
    return []

class FixedOutput(object):
  "Fixed output"

  def gethtml(self, container):
    "Return constant HTML code"
    return container.html

class ContentsOutput(object):
  "Outputs the contents converted to HTML"

  def gethtml(self, container):
    "Return the HTML code"
    html = []
    if container.contents == None:
      return html
    for element in container.contents:
      if not hasattr(element, 'gethtml'):
        Trace.error('No html in ' + element.__class__.__name__ + ': ' + unicode(element))
        return html
      html += element.gethtml()
    return html

class TaggedOutput(ContentsOutput):
  "Outputs an HTML tag surrounding the contents"

  def __init__(self):
    self.breaklines = False

  def settag(self, tag, breaklines=False):
    "Set the value for the tag"
    self.tag = tag
    self.breaklines = breaklines
    return self

  def setbreaklines(self, breaklines):
    "Set the value for breaklines"
    self.breaklines = breaklines
    return self

  def gethtml(self, container):
    "Return the HTML code"
    html = [self.getopen(container)]
    html += ContentsOutput.gethtml(self, container)
    html.append(self.getclose(container))
    return html

  def getopen(self, container):
    "Get opening line"
    if self.tag == '':
      return ''
    open = '<' + self.tag + '>'
    if self.breaklines:
      return '\n' + open + '\n'
    return open

  def getclose(self, container):
    "Get closing line"
    if self.tag == '':
      return ''
    close = '</' + self.tag.split()[0] + '>'
    if self.breaklines:
      return '\n' + close
    return close

class StringOutput(object):
  "Returns a bare string as output"

  def gethtml(self, container):
    "Return a bare string"
    return [container.string]

class HeaderOutput(object):
  "Returns the HTML headers"

  def gethtml(self, container):
    "Return a constant header"
    html = self.getheader(container)
    if Options.jsmath or Options.mathjax:
      html.append(u'<noscript>\n')
      html.append(u'<div class="warning">\n')
      html.append(TranslationConfig.constants['jsmath-warning'])
      if Options.jsmath:
        html.append(u'<a href="http://www.math.union.edu/locate/jsMath">jsMath</a>')
      if Options.mathjax:
        html.append(u'<a href="http://www.mathjax.org/">MathJax</a>')
      html.append(TranslationConfig.constants['jsmath-requires'])
      html.append(TranslationConfig.constants['jsmath-enable'] + '\n')
      html.append(u'</div><hr/>\n')
      html.append(u'</noscript>\n')
    return html

  def getheader(self, container):
    "Get the header part."
    if Options.raw:
      return ['<!--starthtml-->\n']
    if Options.iso885915:
      encoding = 'ISO-8859-1'
    else:
      encoding = 'UTF-8'
    if not Options.html:
      html = [u'<?xml version="1.0" encoding="' + encoding + '"?>\n']
      html.append(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
      html.append(u'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n')
    else:
      html = [u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n']
      html.append(u'<html lang="en">\n')
    html.append(u'<head>\n')
    html.append(u'<meta http-equiv="Content-Type" content="text/html; charset=' + encoding + '"/>\n')
    html.append(u'<meta name="generator" content="http://www.nongnu.org/elyxer/"/>\n')
    html.append(u'<meta name="create-date" content="' + datetime.date.today().isoformat() + '"/>\n')
    html.append(u'<link rel="stylesheet" href="' + Options.css + '" type="text/css" media="screen"/>\n')
    html += TitleOutput().gethtml(container)
    if Options.jsmath:
      html.append(u'<script type="text/javascript" src="' + Options.jsmath + '/plugins/noImageFonts.js"></script>\n')
      html.append(u'<script type="text/javascript" src="' + Options.jsmath + '/easy/load.js"></script>\n')
    if Options.mathjax:
      html.append(u'<script type="text/javascript" src="' + Options.mathjax + '/MathJax.js">\n')
      html.append(u'  //  Load MathJax and get it running\n')
      html.append(u'  MathJax.Hub.Config({ jax: ["input/TeX"],\n') # output/HTML-CSS
      html.append(u'  config: ["MMLorHTML.js"],\n')
      html.append(u'  extensions: ["TeX/AMSmath.js","TeX/AMSsymbols.js"],\n')
      html.append(u'  "HTML-CSS": { imageFont: null }\n')
      html.append(u'  });\n')
      html.append(u'</script>\n')
    html.append(u'<script type="text/javascript" src="scripts/shCore.js"></script>\n')
    html.append(u'<script type="text/javascript" src="scripts/shBrushXml.js"></script>\n')
    html.append(u'<script type="text/javascript" src="scripts/shBrushScala.js"></script>\n')
    html.append(u'<script type="text/javascript" src="scripts/shBrushBash.js"></script>\n')
    html.append(u'<link href="css/shCore.css" rel="stylesheet" type="text/css" />\n')
    html.append(u'<link href="css/shThemeDefault.css" rel="stylesheet" type="text/css" />\n')
    html.append('</head>\n')
    html.append('<body>\n')
    html.append('<div id="globalWrapper">\n')
    if Options.mathjax:
      html.append(u'<script type="math/tex">\n')
      html.append(u'\\newcommand{\\lyxlock}{}\n')
      html.append(u'</script>\n')
    return html

class TitleOutput(object):
  "Return the HTML title tag"

  pdftitle = None
  title = None

  def gethtml(self, container):
    "Return the title tag"
    return ['<title>' + self.gettitle() + '</title>\n']

  def gettitle(self):
    "Return the correct title from the option or the PDF title"
    if Options.title:
      return Options.title
    if TitleOutput.title:
      return TitleOutput.title
    if TitleOutput.pdftitle:
      return TitleOutput.pdftitle
    return 'Converted document'

class FooterOutput(object):
  "Return the HTML code for the footer"

  author = None

  def gethtml(self, container):
    "Footer HTML"
    if Options.raw:
      return ['\n\n<!--endhtml-->']
    html = []
    html.append('\n\n')
    footer = self.createfooter()
    if len(footer) > 0:
      html.append('<hr class="footer"/>\n')
      html += footer
    html.append('</div>\n')
    html.append('<script type="text/javascript">SyntaxHighlighter.all()</script>\n')
    html.append('</body>\n')
    html.append('</html>\n')
    return html

  def createfooter(self):
    "Create the footer proper."
    html = []
    if FooterOutput.author and not Options.nocopy:
      year = datetime.date.today().year
      copyright = '<div class="footer">\nCopyright (C) ' + unicode(year)
      copyright += ' ' + FooterOutput.author + '\n</div>\n'
      html.append(copyright)
    if not Options.nofooter:
      version = GeneralConfig.version['number']
      version += ' (' + GeneralConfig.version['date'] + ')'
      creationdate = '<span class="create-date">' + datetime.datetime.now().isoformat() + '</span>'
      versionp = '<div class="footer" id="generated-by">\nDocument generated by <a href="http://elyxer.nongnu.org/">eLyXer '
      versionp += version + '</a> on ' + creationdate + '\n</div>\n'
      html.append(versionp)
    return html










import sys


class Position(object):
  "A position in a text to parse"

  def __init__(self):
    self.endinglist = EndingList()

  def skip(self, string):
    "Skip a string"
    Trace.error('Unimplemented skip()')

  def identifier(self):
    "Return an identifier for the current position."
    Trace.error('Unimplemented identifier()')
    return 'Error'

  def isout(self):
    "Find out if we are out of the position yet."
    Trace.error('Unimplemented isout()')
    return True

  def current(self):
    "Return the current character"
    Trace.error('Unimplemented current()')
    return ''

  def checkfor(self, string):
    "Check for a string at the given position."
    Trace.error('Unimplemented checkfor()')
    return False

  def finished(self):
    "Find out if the current formula has finished"
    if self.isout():
      self.endinglist.checkpending()
      return True
    return self.endinglist.checkin(self)

  def currentskip(self):
    "Return the current character and skip it."
    current = self.current()
    self.skip(current)
    return current

  def next(self):
    "Advance the position and return the next character."
    self.currentskip()
    return self.current()

  def checkskip(self, string):
    "Check for a string at the given position; if there, skip it"
    if not self.checkfor(string):
      return False
    self.skip(string)
    return True

  def glob(self, currentcheck):
    "Glob a bit of text that satisfies a check"
    glob = ''
    while not self.finished() and currentcheck(self.current()):
      glob += self.current()
      self.skip(self.current())
    return glob

  def globalpha(self):
    "Glob a bit of alpha text"
    return self.glob(lambda current: current.isalpha())

  def checkidentifier(self):
    "Check if the current character belongs to an identifier."
    return self.isidentifier(self.current())

  def isidentifier(self, char):
    "Return if the given character is alphanumeric or _."
    if char.isalnum() or char == '_':
      return True
    return False

  def globidentifier(self):
    "Glob alphanumeric and _ symbols."
    return self.glob(lambda current: self.isidentifier(current))

  def skipspace(self):
    "Skip all whitespace at current position"
    return self.glob(lambda current: current.isspace())

  def globincluding(self, magicchar):
    "Glob a bit of text up to (including) the magic char."
    glob = self.glob(lambda current: current != magicchar) + magicchar
    self.skip(magicchar)
    return glob

  def globexcluding(self, magicchar):
    "Glob a bit of text up until (excluding) the magic char."
    return self.glob(lambda current: current != magicchar)

  def pushending(self, ending, optional = False):
    "Push a new ending to the bottom"
    self.endinglist.add(ending, optional)

  def popending(self, expected = None):
    "Pop the ending found at the current position"
    ending = self.endinglist.pop(self)
    if expected and expected != ending:
      Trace.error('Expected ending ' + expected + ', got ' + ending)
    self.skip(ending)
    return ending

class TextPosition(Position):
  "A parse position based on a raw text."

  def __init__(self, text):
    "Create the position from some text."
    Position.__init__(self)
    self.pos = 0
    self.text = text

  def skip(self, string):
    "Skip a string of characters."
    self.pos += len(string)

  def identifier(self):
    "Return a sample of the remaining text."
    length = 30
    if self.pos + length > len(self.text):
      length = len(self.text) - self.pos - 1
    return '*' + self.text[self.pos:self.pos + length]

  def isout(self):
    "Find out if we are out of the text yet."
    return self.pos >= len(self.text)

  def current(self):
    "Return the current character, assuming we are not out."
    return self.text[self.pos]

  def checkfor(self, string):
    "Check for a string at the given position."
    if self.pos + len(string) > len(self.text):
      return False
    return self.text[self.pos : self.pos + len(string)] == string

class FilePosition(Position):
  "A parse position based on an underlying file."

  def __init__(self, filename):
    "Create the position from a file."
    Position.__init__(self)
    self.reader = LineReader(filename)
    self.number = 1
    self.pos = 0

  def skip(self, string):
    "Skip a string of characters."
    length = len(string)
    while self.pos + length > len(self.reader.currentline()):
      length -= len(self.reader.currentline()) - self.pos + 1
      self.nextline()
    self.pos += length

  def nextline(self):
    "Go to the next line."
    self.reader.nextline()
    self.number += 1
    self.pos = 0

  def identifier(self):
    "Return the current line and line number in the file."
    before = self.reader.currentline()[:self.pos - 1]
    after = self.reader.currentline()[self.pos:]
    return 'line ' + unicode(self.number) + ': ' + before + '*' + after

  def isout(self):
    "Find out if we are out of the text yet."
    if self.pos > len(self.reader.currentline()):
      if self.pos > len(self.reader.currentline()) + 1:
        Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      self.nextline()
    return self.reader.finished()

  def current(self):
    "Return the current character, assuming we are not out."
    if self.pos == len(self.reader.currentline()):
      return '\n'
    if self.pos > len(self.reader.currentline()):
      Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      return '*'
    return self.reader.currentline()[self.pos]

  def checkfor(self, string):
    "Check for a string at the given position."
    if self.pos + len(string) > len(self.reader.currentline()):
      return False
    return self.reader.currentline()[self.pos : self.pos + len(string)] == string

class EndingList(object):
  "A list of position endings"

  def __init__(self):
    self.endings = []

  def add(self, ending, optional):
    "Add a new ending to the list"
    self.endings.append(PositionEnding(ending, optional))

  def checkin(self, pos):
    "Search for an ending"
    if self.findending(pos):
      return True
    return False

  def pop(self, pos):
    "Remove the ending at the current position"
    ending = self.findending(pos)
    if not ending:
      Trace.error('No ending at ' + pos.current())
      return ''
    for each in reversed(self.endings):
      self.endings.remove(each)
      if each == ending:
        return each.ending
      elif not each.optional:
        Trace.error('Removed non-optional ending ' + each)
    Trace.error('No endings left')
    return ''

  def findending(self, pos):
    "Find the ending at the current position"
    if len(self.endings) == 0:
      return None
    for index, ending in enumerate(reversed(self.endings)):
      if ending.checkin(pos):
        return ending
      if not ending.optional:
        return None
    return None

  def checkpending(self):
    "Check if there are any pending endings"
    if len(self.endings) != 0:
      Trace.error('Pending ' + unicode(self) + ' left open')

  def __unicode__(self):
    "Printable representation"
    string = 'endings ['
    for ending in self.endings:
      string += unicode(ending) + ','
    if len(self.endings) > 0:
      string = string[:-1]
    return string + ']'

class PositionEnding(object):
  "An ending for a parsing position"

  def __init__(self, ending, optional):
    self.ending = ending
    self.optional = optional

  def checkin(self, pos):
    "Check for the ending"
    return pos.checkfor(self.ending)

  def __unicode__(self):
    "Printable representation"
    string = 'Ending ' + self.ending
    if self.optional:
      string += ' (optional)'
    return string



class Container(object):
  "A container for text and objects in a lyx file"

  def __init__(self):
    self.contents = list()

  def process(self):
    "Process contents"
    pass

  def gethtml(self):
    "Get the resulting HTML"
    html = self.output.gethtml(self)
    if isinstance(html, basestring):
      Trace.error('Raw string ' + html)
      html = [html]
    return self.escapeall(html)

  def escapeall(self, lines):
    "Escape all lines in an array according to the output options."
    result = []
    for line in lines:
      if Options.html:
        line = self.escape(line, EscapeConfig.html)
      if Options.iso885915:
        line = self.escape(line, EscapeConfig.iso885915)
        line = self.escapeentities(line)
      elif not Options.unicode:
        line = self.escape(line, EscapeConfig.nonunicode)
      result.append(line)
    return result

  def escape(self, line, replacements = EscapeConfig.entities):
    "Escape a line with replacements from a map"
    pieces = replacements.keys()
    # do them in order
    pieces.sort()
    for piece in pieces:
      if piece in line:
        line = line.replace(piece, replacements[piece])
    return line

  def escapeentities(self, line):
    "Escape all Unicode characters to HTML entities."
    result = ''
    pos = TextPosition(line)
    while not pos.finished():
      if ord(pos.current()) > 128:
        codepoint = hex(ord(pos.current()))
        if codepoint == '0xd835':
          codepoint = hex(ord(pos.next()) + 0xf800)
        result += '&#' + codepoint[1:] + ';'
      else:
        result += pos.current()
      pos.currentskip()
    return result

  def searchall(self, type):
    "Search for all embedded containers of a given type"
    list = []
    self.searchprocess(type, lambda container: list.append(container))
    return list

  def searchremove(self, type):
    "Search for all containers of a type and remove them"
    list = []
    self.searchprocess(type, lambda container: self.appendremove(list, container))
    return list

  def appendremove(self, list, container):
    "Append to a list and remove from own contents"
    list.append(container)
    container.parent.contents.remove(container)

  def searchprocess(self, type, process):
    "Search for elements of a given type and process them"
    self.locateprocess(lambda container: isinstance(container, type), process)

  def locateprocess(self, locate, process):
    "Search for all embedded containers and process them"
    for container in self.contents:
      container.locateprocess(locate, process)
      if locate(container):
        process(container)

  def extracttext(self):
    "Search for all the strings and extract the text they contain"
    text = ''
    strings = self.searchall(StringContainer)
    for string in strings:
      text += string.string
    return text

  def group(self, index, group, isingroup):
    "Group some adjoining elements into a group"
    if index >= len(self.contents):
      return
    if hasattr(self.contents[index], 'grouped'):
      return
    while index < len(self.contents) and isingroup(self.contents[index]):
      self.contents[index].grouped = True
      group.contents.append(self.contents[index])
      self.contents.pop(index)
    self.contents.insert(index, group)

  def remove(self, index):
    "Remove a container but leave its contents"
    container = self.contents[index]
    self.contents.pop(index)
    while len(container.contents) > 0:
      self.contents.insert(index, container.contents.pop())

  def debug(self, level = 0):
    "Show the contents in debug mode"
    if not Trace.debugmode:
      return
    Trace.debug('  ' * level + unicode(self))
    for element in self.contents:
      element.debug(level + 1)

  def tree(self, level = 0):
    "Show in a tree"
    Trace.debug("  " * level + unicode(self))
    for container in self.contents:
      container.tree(level + 1)

  def __unicode__(self):
    "Get a description"
    if not hasattr(self, 'begin'):
      return self.__class__.__name__
    return self.__class__.__name__ + '@' + unicode(self.begin)

class BlackBox(Container):
  "A container that does not output anything"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = EmptyOutput()
    self.contents = []

class LyXFormat(BlackBox):
  "Read the lyxformat command"

  def process(self):
    "Show warning if version < 276"
    version = int(self.header[1])
    if version < 276:
      Trace.error('Warning: unsupported format version ' + str(version))

class StringContainer(Container):
  "A container for a single string"

  def __init__(self):
    self.parser = StringParser()
    self.output = StringOutput()
    self.string = ''

  def process(self):
    "Replace special chars from the contents."
    if len(self.contents) > 0:
      self.string = self.replacespecial(self.contents[0])
      self.contents = []

  def replacespecial(self, line):
    "Replace all special chars from a line"
    replaced = self.escape(line, EscapeConfig.entities)
    replaced = self.changeline(replaced)
    if ContainerConfig.string['startcommand'] in replaced and len(replaced) > 1:
      # unprocessed commands
      message = 'Unknown command at ' + unicode(self.parser.begin) + ': '
      Trace.error(message + replaced.strip())
    return replaced

  def changeline(self, line):
    line = self.escape(line, EscapeConfig.chars)
    if not ContainerConfig.string['startcommand'] in line:
      return line
    line = self.escape(line, EscapeConfig.commands)
    return line
  
  def __unicode__(self):
    result = 'StringContainer@' + unicode(self.begin)
    ellipsis = '...'
    if len(self.string.strip()) <= 15:
      ellipsis = ''
    return result + ' (' + self.string.strip()[:15] + ellipsis + ')'

class Constant(StringContainer):
  "A constant string"

  def __init__(self, text):
    self.contents = []
    self.string = text
    self.output = StringOutput()

  def __unicode__(self):
    return 'Constant: ' + self.string

class TaggedText(Container):
  "Text inside a tag"

  def __init__(self):
    ending = None
    if self.__class__.__name__ in ContainerConfig.endings:
      ending = ContainerConfig.endings[self.__class__.__name__]
    self.parser = TextParser(ending)
    self.output = TaggedOutput()

  def complete(self, contents, tag, breaklines=False):
    "Complete the tagged text and return it"
    self.contents = contents
    self.output.tag = tag
    self.output.breaklines = breaklines
    return self

  def constant(self, text, tag, breaklines=False):
    "Complete the tagged text with a constant"
    constant = Constant(text)
    return self.complete([constant], tag, breaklines)

  def __unicode__(self):
    return 'Tagged <' + self.output.tag + '>'



class QuoteContainer(Container):
  "A container for a pretty quote"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.type = self.header[2]
    if not self.type in StyleConfig.quotes:
      Trace.error('Quote type ' + self.type + ' not found')
      self.html = ['"']
      return
    self.html = [StyleConfig.quotes[self.type]]

class LyXLine(Container):
  "A Lyx line"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    self.html = ['<hr class="line" />']

class EmphaticText(TaggedText):
  "Text with emphatic mode"

  def process(self):
    self.output.tag = 'i'

class ShapedText(TaggedText):
  "Text shaped (italic, slanted)"

  def process(self):
    self.type = self.header[1]
    if not self.type in TagConfig.shaped:
      Trace.error('Unrecognized shape ' + self.header[1])
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.shaped[self.type]

class VersalitasText(TaggedText):
  "Text in versalitas"

  def process(self):
    self.output.tag = 'span class="versalitas"'

class ColorText(TaggedText):
  "Colored text"

  def process(self):
    self.color = self.header[1]
    self.output.tag = 'span class="' + self.color + '"'

class SizeText(TaggedText):
  "Sized text"

  def process(self):
    self.size = self.header[1]
    self.output.tag = 'span class="' + self.size + '"'

class BoldText(TaggedText):
  "Bold text"

  def process(self):
    self.output.tag = 'b'

class TextFamily(TaggedText):
  "A bit of text from a different family"

  def process(self):
    "Parse the type of family"
    self.type = self.header[1]
    if not self.type in TagConfig.family:
      Trace.error('Unrecognized family ' + type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.family[self.type]

class Hfill(TaggedText):
  "Horizontall fill"

  def process(self):
    Trace.debug('hfill')
    self.output.tag = 'span class="hfill"'

class BarredText(TaggedText):
  "Text with a bar somewhere"

  def process(self):
    "Parse the type of bar"
    self.type = self.header[1]
    if not self.type in TagConfig.barred:
      Trace.error('Unknown bar type ' + self.type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.barred[self.type]

class LangLine(Container):
  "A line with language information"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = EmptyOutput()

  def process(self):
    self.lang = self.header[1]

class Space(Container):
  "A space of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()
  
  def process(self):
    self.type = self.header[2]
    if self.type not in StyleConfig.spaces:
      Trace.error('Unknown space type ' + self.type)
      self.html = [' ']
      return
    self.html = [StyleConfig.spaces[self.type]]








import gettext


class Translator(object):
  "Reads the configuration file and tries to find a translation."
  "Otherwise falls back to the messages in the config file."

  instance = None
  language = None

  def translate(cls, key):
    "Get the translated message for a key."
    return cls.instance.getmessage(key)

  translate = classmethod(translate)

  def __init__(self):
    self.translation = None
    self.first = True

  def findtranslation(self):
    "Find the translation for the document language."
    self.langcodes = None
    if not self.language:
      Trace.error('No language in document')
      return
    if not self.language in TranslationConfig.languages:
      Trace.error('Unknown language ' + self.language)
      return
    if TranslationConfig.languages[self.language] == 'en':
      return
    langcodes = [TranslationConfig.languages[self.language]]
    try:
      self.translation = gettext.translation('elyxer', None, langcodes)
    except IOError:
      Trace.error('No translation for ' + unicode(langcodes))

  def getmessage(self, key):
    "Get the translated message for the given key."
    if self.first:
      self.findtranslation()
      self.first = False
    message = self.getuntranslated(key)
    if not self.translation:
      return message
    try:
      message = self.translation.ugettext(message)
    except IOError:
      pass
    return message

  def getuntranslated(self, key):
    "Get the untranslated message."
    return TranslationConfig.constants[key]

Translator.instance = Translator()

class TranslationExport(object):
  "Export the translation to a file."

  def __init__(self, writer):
    self.writer = writer

  def export(self, constants):
    "Export the translation constants as a .po file."
    self.writer.writeline('# SOME DESCRIPTIVE TITLE.')
    self.writer.writeline('# eLyXer version ' + GeneralConfig.version['number'])
    self.writer.writeline('# Released on ' + GeneralConfig.version['date'])
    self.writer.writeline(u'# Contact: Alex Fernández <elyxer@gmail.com>')
    self.writer.writeline('# This file is distributed under the same license as the eLyXer package.')
    self.writer.writeline('# (C) YEAR FIRST AUTHOR <EMAIL@ADDRESS>.')
    self.writer.writeline('#')
    self.writer.writeline('#, fuzzy')
    self.writer.writeline('msgid ""')
    self.writer.writeline('msgstr ""')
    self.writer.writeline('')
    for key, message in constants.iteritems():
      self.writer.writeline('')
      self.writer.writeline('#: ' + key)
      self.writer.writeline('msgid  "' + message + '"')
      self.writer.writeline('msgstr "' + message + '"')
    self.writer.close()



class Link(Container):
  "A link to another part of the document"

  def __init__(self):
    Container.__init__(self)
    self.parser = InsetParser()
    self.output = LinkOutput()
    self.anchor = None
    self.url = None
    self.type = None
    self.page = None
    self.target = None
    self.destination = None
    self.title = None
    if Options.target:
      self.target = Options.target

  def complete(self, text, anchor = None, url = None, type = None, title = None):
    "Complete the link."
    self.contents = [Constant(text)]
    if anchor:
      self.anchor = anchor
    if url:
      self.url = url
    if type:
      self.type = type
    if title:
      self.title = title
    return self

  def computedestination(self):
    "Use the destination link to fill in the destination URL."
    if not self.destination:
      return
    self.url = ''
    if self.destination.anchor:
      self.url = '#' + self.destination.anchor
    if self.destination.page:
      self.url = self.destination.page + self.url

  def setmutualdestination(self, destination):
    "Set another link as destination, and set its destination to this one."
    self.destination = destination
    destination.destination = self

class ListInset(Container):
  "An inset with a list, normally made of links."

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def sortdictionary(self, dictionary):
    "Sort all entries in the dictionary"
    keys = dictionary.keys()
    # sort by name
    keys.sort()
    return keys

class ListOf(ListInset):
  "A list of entities (figures, tables, algorithms)"

  def process(self):
    "Parse the header and get the type"
    self.type = self.header[2]
    text = Translator.translate('list-' + self.type)
    self.contents = [TaggedText().constant(text, 'div class="tocheader"', True)]

class TableOfContents(ListInset):
  "Table of contents"

  def process(self):
    "Parse the header and get the type"
    text = Translator.translate('toc')
    self.contents = [TaggedText().constant(text, 'div class="tocheader"', True)]

class IndexEntry(Link):
  "An entry in the alphabetical index"

  entries = dict()
  arrows = dict()

  namescapes = {'!':'', '|':', ', '  ':' '}
  keyescapes = {' ':'-', '--':'-', ',':''}

  def process(self):
    "Put entry in index"
    if 'name' in self.parameters:
      name = self.parameters['name'].strip()
    else:
      name = self.extracttext()
    self.name = self.escape(name, IndexEntry.namescapes)
    key = self.escape(self.name, IndexEntry.keyescapes)
    if not key in IndexEntry.entries:
      # no entry yet; create
      entry = Link().complete(name, 'index-' + key, None, 'printindex')
      entry.name = name
      IndexEntry.entries[key] = entry
    if not key in IndexEntry.arrows:
      # no arrows yet; create list
      IndexEntry.arrows[key] = []
    self.index = len(IndexEntry.arrows[key])
    self.complete(u'↓', 'entry-' + key + '-' + unicode(self.index))
    self.destination = IndexEntry.entries[key]
    arrow = Link().complete(u'↑', 'index-' + key)
    arrow.destination = self
    IndexEntry.arrows[key].append(arrow)

class PrintIndex(ListInset):
  "Command to print an index"

  def process(self):
    "Create the alphabetic index"
    index = Translator.translate('index')
    self.contents = [TaggedText().constant(index, 'h1 class="index"'),
        Constant('\n')]
    for key in self.sortdictionary(IndexEntry.entries):
      entry = IndexEntry.entries[key]
      entrytext = [IndexEntry.entries[key], Constant(': ')]
      contents = [TaggedText().complete(entrytext, 'i')]
      contents += self.extractarrows(key)
      self.contents.append(TaggedText().complete(contents, 'p class="printindex"',
          True))

  def extractarrows(self, key):
    "Extract all arrows (links to the original reference) for a key."
    arrows = []
    for arrow in IndexEntry.arrows[key]:
      arrows += [arrow, Constant(u', \n')]
    return arrows[:-1]

class NomenclatureEntry(Link):
  "An entry of LyX nomenclature"

  entries = dict()

  def process(self):
    "Put entry in index"
    symbol = self.parameters['symbol']
    description = self.parameters['description']
    key = symbol.replace(' ', '-').lower()
    if key in NomenclatureEntry.entries:
      Trace.error('Duplicated nomenclature entry ' + key)
    self.complete(u'↓', 'noment-' + key)
    entry = Link().complete(u'↑', 'nom-' + key)
    entry.symbol = symbol
    entry.description = description
    self.setmutualdestination(entry)
    NomenclatureEntry.entries[key] = entry

class PrintNomenclature(ListInset):
  "Print all nomenclature entries"

  def process(self):
    nomenclature = Translator.translate('nomenclature')
    self.contents = [TaggedText().constant(nomenclature,
      'h1 class="nomenclature"')]
    for key in self.sortdictionary(NomenclatureEntry.entries):
      entry = NomenclatureEntry.entries[key]
      contents = [entry, Constant(entry.symbol + u' ' + entry.description)]
      text = TaggedText().complete(contents, 'div class="Nomenclated"', True)
      self.contents.append(text)

class URL(Link):
  "A clickable URL"

  def process(self):
    "Read URL from parameters"
    name = self.escape(self.parameters['target'])
    if 'type' in self.parameters:
      self.url = self.escape(self.parameters['type']) + name
    else:
      self.url = name
    if 'name' in self.parameters:
      name = self.parameters['name']
    self.contents = [Constant(name)]

class FlexURL(URL):
  "A flexible URL"

  def process(self):
    "Read URL from contents"
    self.url = self.extracttext()

class LinkOutput(object):
  "A link pointing to some destination"
  "Or an anchor (destination)"

  def gethtml(self, link):
    "Get the HTML code for the link"
    type = link.__class__.__name__
    if link.type:
      type = link.type
    tag = 'a class="' + type + '"'
    if link.anchor:
      tag += ' name="' + link.anchor + '"'
    if link.destination:
      link.computedestination()
    if link.url:
      tag += ' href="' + link.url + '"'
    if link.target:
      tag += ' target="' + link.target + '"'
    if link.title:
      tag += ' title="' + link.title + '"'
    text = TaggedText().complete(link.contents, tag)
    return text.gethtml()









class NumberGenerator(object):
  "A number generator for unique sequences and hierarchical structures"

  letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

  instance = None
  startinglevel = 0
  maxdepth = 10

  unique = NumberingConfig.layouts['unique']
  ordered = NumberingConfig.layouts['ordered']

  def __init__(self):
    self.number = []
    self.uniques = dict()
    self.chaptered = dict()

  def generateunique(self, type):
    "Generate unique numbering: a number to place in the title but not to "
    "append to others. Examples: Part 1, Book 3."
    if not type in self.uniques:
      self.uniques[type] = 0
    self.uniques[type] = self.increase(self.uniques[type])
    return unicode(self.uniques[type])

  def generateordered(self, type):
    "Generate ordered numbering: a number to use and possibly concatenate "
    "with others. Example: Chapter 1, Section 1.5."
    level = self.getlevel(type)
    if level == 0:
      Trace.error('Impossible level 0 for ' + type)
      return '.'
    if len(self.number) >= level:
      self.number = self.number[:level]
    else:
      while len(self.number) < level:
        self.number.append(0)
    self.number[level - 1] = self.increase(self.number[level - 1])
    return self.dotseparated(self.number)

  def generatechaptered(self, type, chapter = None):
    "Generate a number which goes with first-level numbers (chapters). "
    "For the article classes a unique number is generated."
    if NumberGenerator.startinglevel > 0:
      return self.generateunique(type)
    if not chapter:
      chapter = self.getchapter()
    if not type in self.chaptered or self.chaptered[type][0] != chapter:
      self.chaptered[type] = [chapter, 0]
    chaptered = self.chaptered[type]
    chaptered[1] = self.increase(chaptered[1])
    self.chaptered[type] = chaptered
    return self.dotseparated(chaptered)

  def getchapter(self):
    "Get the current chapter number."
    if len(self.number) == 0:
      return 0
    else:
      return self.number[0]

  def getlevel(self, type):
    "Get the level that corresponds to a type."
    type = self.deasterisk(type)
    if type in NumberGenerator.unique:
      return 0
    level = NumberGenerator.ordered.index(type) + 1
    return level - NumberGenerator.startinglevel

  def isunique(self, container):
    "Find out if a container requires unique numbering."
    return self.deasterisk(container.type) in NumberGenerator.unique

  def isinordered(self, container):
    "Find out if a container is ordered or unordered."
    return self.deasterisk(container.type) in NumberGenerator.ordered

  def isnumbered(self, container):
    "Find out if a container is numbered."
    if '*' in container.type:
      return False
    if self.getlevel(container.type) > NumberGenerator.maxdepth:
      return False
    return True

  def increase(self, number):
    "Increase the number (or letter)"
    if not isinstance(number, str):
      return number + 1
    if number == '-':
      index = 0
    elif not number in NumberGenerator.letters:
      Trace.error('Unknown letter numeration ' + number)
      return 0
    else:
      index = NumberGenerator.letters.index(number) + 1
    return self.letter(index)

  def letter(self, index):
    "Get the letter that corresponds to the given index."
    return NumberGenerator.letters[index % len(NumberGenerator.letters)]

  def dotseparated(self, number):
    "Get the number separated by dots: 1.1.3"
    dotsep = ''
    if len(number) == 0:
      Trace.error('Empty number')
      return '.'
    for piece in number:
      dotsep += '.' + unicode(piece)
    return dotsep[1:]

  def deasterisk(self, type):
    "Get the type without the asterisk for unordered types."
    return type.replace('*', '')

NumberGenerator.instance = NumberGenerator()

class LayoutNumberer(object):
  "Number a layout with the relevant attributes."

  instance = None

  def __init__(self):
    self.generator = NumberGenerator.instance
    self.lastnumbered = None

  def isnumbered(self, container):
    "Find out if a container requires numbering at all."
    return self.generator.isinordered(container) or self.generator.isunique(container)

  def numberlayout(self, layout):
    "Set all attributes: number, entry, level..."
    if self.generator.isunique(layout):
      number = self.generator.generateunique(layout.type)
      self.setcommonattrs(layout, number)
      layout.anchortext = ''
      if layout.number != '':
        layout.anchortext = layout.entry + '.'
      return
    if not self.generator.isinordered(layout):
      Trace.error('Trying to number wrong ' + unicode(layout))
      return
    # ordered or unordered
    if self.generator.isnumbered(layout):
      number = self.generator.generateordered(layout.type)
    else:
      number = self.generator.generateunique(layout.type)
    self.setcommonattrs(layout, number)
    layout.anchortext = layout.number
    layout.output.tag = layout.output.tag.replace('?', unicode(layout.level))

  def setcommonattrs(self, layout, number):
    "Set the common attributes for a layout."
    layout.level = self.generator.getlevel(layout.type)
    type = self.generator.deasterisk(layout.type)
    layout.number = ''
    if self.generator.isnumbered(layout):
      layout.number = number
    layout.partkey = 'toc-' + layout.type + '-' + number
    layout.entry = Translator.translate(type)
    if layout.number != '':
      self.lastnumbered = layout
      layout.entry += ' ' + layout.number

LayoutNumberer.instance = LayoutNumberer()






class Postprocessor(object):
  "Postprocess a container keeping some context"

  stages = []

  def __init__(self):
    self.stages = StageDict(Postprocessor.stages, self)
    self.current = None
    self.last = None

  def postprocess(self, next):
    "Postprocess the root container and its contents"
    self.postrecursive(self.current)
    result = self.postcurrent(next)
    self.last = self.current
    self.current = next
    return result

  def postrecursive(self, container):
    "Postprocess the container contents recursively"
    if not hasattr(container, 'contents'):
      return
    if len(container.contents) == 0:
      return
    if hasattr(container, 'postprocess'):
      if not container.postprocess:
        return
    postprocessor = Postprocessor()
    contents = []
    for element in container.contents:
      post = postprocessor.postprocess(element)
      if post:
        contents.append(post)
    # two rounds to empty the pipeline
    for i in range(2):
      post = postprocessor.postprocess(None)
      if post:
        contents.append(post)
    container.contents = contents

  def postcurrent(self, next):
    "Postprocess the current element taking into account next and last."
    stage = self.stages.getstage(self.current)
    if not stage:
      return self.current
    return stage.postprocess(self.last, self.current, next)

class StageDict(object):
  "A dictionary of stages corresponding to classes"

  def __init__(self, classes, postprocessor):
    "Instantiate an element from each class and store as a dictionary"
    instances = self.instantiate(classes, postprocessor)
    self.stagedict = dict([(x.processedclass, x) for x in instances])

  def instantiate(self, classes, postprocessor):
    "Instantiate an element from each class"
    stages = [x.__new__(x) for x in classes]
    for element in stages:
      element.__init__()
      element.postprocessor = postprocessor
    return stages

  def getstage(self, element):
    "Get the stage for a given element, if the type is in the dict"
    if not element.__class__ in self.stagedict:
      return None
    return self.stagedict[element.__class__]



class Label(Link):
  "A label to be referenced"

  names = dict()

  def process(self):
    "Process a label container."
    key = self.parameters['name']
    self.create(' ', key)

  def create(self, text, key, type = 'Label'):
    "Create the label for a given key."
    self.key = key
    self.complete(text, anchor = key, type = type)
    Label.names[key] = self
    if key in Reference.references:
      for reference in Reference.references[key]:
        reference.destination = self
    return self

  def labelnumber(self):
    "Get the number for the latest numbered container seen."
    numbered = self.numbered(self)
    if numbered and numbered.number:
      return numbered.number
    return ''

  def numbered(self, container):
    "Get the numbered container for the label."
    if hasattr(container, 'number'):
      return container
    if not hasattr(container, 'parent'):
      if hasattr(self, 'lastnumbered'):
        return self.lastnumbered
      return None
    return self.numbered(container.parent)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self, 'key'):
      return 'Unnamed label'
    return 'Label ' + self.key

class Reference(Link):
  "A reference to a label."

  references = dict()
  formats = {
      'ref':u'@↕', 'eqref':u'(@↕)', 'pageref':u'#↕',
      'vref':u'@on-page#↕'
      }

  def process(self):
    "Read the reference and set the arrow."
    self.key = self.parameters['reference']
    if self.key in Label.names:
      self.direction = u'↑'
      label = Label.names[self.key]
    else:
      self.direction = u'↓'
      label = Label().complete(' ', self.key, 'preref')
    self.destination = label
    self.format()
    if not self.key in Reference.references:
      Reference.references[self.key] = []
    Reference.references[self.key].append(self)

  def format(self):
    "Format the reference contents."
    if 'LatexCommand' in self.parameters:
      formatkey = self.parameters['LatexCommand']
    else:
      formatkey = 'ref'
    if not formatkey in self.formats:
      Trace.error('Unknown reference format ' + formatkey)
      formatstring = u'↕'
    else:
      formatstring = self.formats[formatkey]
    formatstring = formatstring.replace(u'↕', self.direction)
    formatstring = formatstring.replace('@', self.destination.labelnumber())
    formatstring = formatstring.replace('#', '1')
    formatstring = formatstring.replace('on-page', Translator.translate('on-page'))
    self.contents = [Constant(formatstring)]

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference ' + self.key

class PostLabel(object):
  "Postprocessing of a label: assign number of the referenced part."

  processedclass = Label

  def postprocess(self, last, label, next):
    "Remember the last numbered container seen."
    label.lastnumbered = LayoutNumberer.instance.lastnumbered
    return label

Postprocessor.stages += [PostLabel]













import codecs


class HeaderParser(Parser):
  "Parses the LyX header"

  def parse(self, reader):
    "Parse header parameters into a dictionary"
    self.parseending(reader, lambda: self.parseline(reader))
    # skip last line
    reader.nextline()
    return []

  def parseline(self, reader):
    "Parse a single line as a parameter or as a start"
    line = reader.currentline()
    if line.startswith(HeaderConfig.parameters['branch']):
      self.parsebranch(reader)
      return
    elif line.startswith(HeaderConfig.parameters['lstset']):
      LstParser().parselstset(reader)
      return
    elif line.startswith(HeaderConfig.parameters['beginpreamble']):
      PreambleParser().parsepreamble(reader)
      return
    # no match
    self.parseparameter(reader)

  def parsebranch(self, reader):
    "Parse all branch definitions."
    branch = reader.currentline().split()[1]
    reader.nextline()
    subparser = HeaderParser().complete(HeaderConfig.parameters['endbranch'])
    subparser.parse(reader)
    options = BranchOptions(branch)
    for key in subparser.parameters:
      options.set(key, subparser.parameters[key])
    Options.branches[branch] = options

  def complete(self, ending):
    "Complete the parser with the given ending."
    self.ending = ending
    return self

class PreambleParser(Parser):
  "A parser for the LyX preamble."

  preamble = []
  parsed = False

  def __init__(self):
    self.ending = HeaderConfig.parameters['endpreamble']

  def parsepreamble(self, reader):
    "Parse the full preamble with all statements."
    reader.nextline()
    self.parseending(reader, lambda: self.parsepreambleline(reader))

  def parsepreambleline(self, reader):
    "Parse a single preamble line."
    PreambleParser.preamble.append(reader.currentline())
    reader.nextline()

class LstParser(object):
  "Parse global and local lstparams."

  globalparams = dict()

  def parselstset(self, reader):
    "Parse a declaration of lstparams in lstset."
    paramtext = self.extractlstset(reader)
    if not '{' in paramtext:
      Trace.error('Missing opening bracket in lstset: ' + paramtext)
      return
    lefttext = paramtext.split('{')[1]
    croppedtext = lefttext[:-1]
    LstParser.globalparams = self.parselstparams(croppedtext)

  def extractlstset(self, reader):
    "Extract the global lstset parameters."
    paramtext = ''
    while not reader.finished():
      paramtext += reader.currentline()
      reader.nextline()
      if paramtext.endswith('}'):
        return paramtext
    Trace.error('Could not find end of \\lstset settings; aborting')

  def parsecontainer(self, container):
    "Parse some lstparams from a container."
    container.lstparams = LstParser.globalparams.copy()
    if not 'lstparams' in container.parameters:
      return
    paramtext = container.parameters['lstparams']
    container.lstparams.update(self.parselstparams(paramtext))

  def parselstparams(self, text):
    "Parse a number of lstparams from a text."
    paramdict = dict()
    paramlist = text.split(',')
    for param in paramlist:
      if not '=' in param:
        if len(param.strip()) > 0:
          Trace.error('Invalid listing parameter ' + param)
      else:
        key, value = param.split('=', 1)
        paramdict[key] = value
    return paramdict




class LyXHeader(Container):
  "Reads the header, outputs the HTML header"

  indentstandard = False
  tocdepth = 10

  def __init__(self):
    self.contents = []
    self.parser = HeaderParser()
    self.output = HeaderOutput()

  def process(self):
    "Find pdf title"
    TitleOutput.pdftitle = self.getparameter('pdftitle')
    if self.getparameter('documentclass') in HeaderConfig.styles['article']:
      NumberGenerator.startinglevel = 1
    if self.getparameter('paragraphseparation') == 'indent':
      LyXHeader.indentstandard = True
    LyXHeader.tocdepth = self.getlevel('tocdepth')
    NumberGenerator.maxdepth = self.getlevel('secnumdepth')
    Translator.language = self.getparameter('language')

  def getparameter(self, configparam):
    "Get a parameter configured in HeaderConfig."
    key = HeaderConfig.parameters[configparam]
    if not key in self.parameters:
      return None
    return self.parameters[key]

  def getlevel(self, configparam):
    "Get a level read as a parameter from HeaderConfig."
    value = int(self.getparameter(configparam))
    if NumberGenerator.startinglevel == 1:
      return value
    return value + 1

class LyXFooter(Container):
  "Reads the footer, outputs the HTML footer"

  def __init__(self):
    self.contents = []
    self.parser = BoundedDummy()
    self.output = FooterOutput()

class Align(Container):
  "Bit of aligned text"

  def __init__(self):
    self.parser = ExcludingParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.output.tag = 'div class="' + self.header[1] + '"'

class Newline(Container):
  "A newline"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.html = ['<br/>\n']

class NewPage(Newline):
  "A new page"

  def process(self):
    "Process contents"
    self.html = ['<p><br/>\n</p>\n']

class Appendix(Container):
  "An appendix to the main document"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = EmptyOutput()

class ERT(Container):
  "Evil Red Text"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()



class Layout(Container):
  "A layout (block of text) inside a lyx file"

  def __init__(self):
    self.contents = list()
    self.parser = BoundedParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.type = self.header[1]
    if self.type in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type] + ' class="' + self.type + '"'
    elif self.type.replace('*', '') in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type.replace('*', '')] + ' class="' +  self.type.replace('*', '-') + '"'
    else:
      self.output.tag = 'div class="' + self.type + '"'
    self.numerate()

  def numerate(self):
    "Numerate if necessary."
    if not LayoutNumberer.instance.isnumbered(self):
      return
    if self.containsappendix():
      self.activateappendix()
    LayoutNumberer.instance.numberlayout(self)

  def containsappendix(self):
    "Find out if there is an appendix somewhere in the layout"
    for element in self.contents:
      if isinstance(element, Appendix):
        return True
    return False
    
  def activateappendix(self):
    "Change first number to letter, and chapter to appendix"
    NumberGenerator.instance.number = ['-']

  def __unicode__(self):
    return 'Layout of type ' + self.type

class StandardLayout(Layout):
  "A standard layout -- can be a true div or nothing at all"

  indentation = False

  def process(self):
    self.type = 'standard'
    self.output = ContentsOutput()

  def complete(self, contents):
    "Set the contents and return it."
    self.process()
    self.contents = contents
    return self

class Title(Layout):
  "The title of the whole document"

  def process(self):
    self.type = 'title'
    self.output.tag = 'h1 class="title"'
    self.title = self.extracttext()
    TitleOutput.title = self.title
    Trace.message('Title: ' + self.title)

class Author(Layout):
  "The document author"

  def process(self):
    self.type = 'author'
    self.output.tag = 'h2 class="author"'
    strings = self.searchall(StringContainer)
    if len(strings) > 0:
      FooterOutput.author = strings[0].string
      Trace.debug('Author: ' + FooterOutput.author)

class Abstract(Layout):
  "A paper abstract"

  def process(self):
    self.type = 'abstract'
    self.output.tag = 'div class="abstract"'
    message = Translator.translate('abstract')
    tagged = TaggedText().constant(message, 'p class="abstract-message"', True)
    self.contents.insert(0, tagged)

class FirstWorder(Layout):
  "A layout where the first word is extracted"

  def extractfirstword(self, contents):
    "Extract the first word as a list"
    first, found = self.extractfirsttuple(contents)
    return first

  def extractfirsttuple(self, contents):
    "Extract the first word as a tuple"
    firstcontents = []
    index = 0
    while index < len(contents):
      first, found = self.extractfirstcontainer(contents[index])
      if first:
        firstcontents += first
      if found:
        return firstcontents, True
      else:
        del contents[index]
    return firstcontents, False

  def extractfirstcontainer(self, container):
    "Extract the first word from a string container"
    if isinstance(container, StringContainer):
      return self.extractfirststring(container)
    if isinstance(container, ERT):
      return [container], False
    if len(container.contents) == 0:
      # empty container
      return [container], False
    first, found = self.extractfirsttuple(container.contents)
    if isinstance(container, TaggedText) and hasattr(container, 'tag'):
      newtag = TaggedText().complete(first, container.tag)
      return [newtag], found
    return first, found

  def extractfirststring(self, container):
    "Extract the first word from a string container"
    string = container.string
    if not ' ' in string:
      return [container], False
    split = string.split(' ', 1)
    container.string = split[1]
    return [Constant(split[0])], True

class Description(FirstWorder):
  "A description layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'Description'
    self.output.tag = 'div class="Description"'
    firstword = self.extractfirstword(self.contents)
    if not firstword:
      return
    firstword.append(Constant(u' '))
    tag = 'span class="Description-entry"'
    self.contents.insert(0, TaggedText().complete(firstword, tag))

class List(FirstWorder):
  "A list layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'List'
    self.output.tag = 'div class="List"'
    firstword = self.extractfirstword(self.contents)
    if not firstword:
      return
    first = TaggedText().complete(firstword, 'span class="List-entry"')
    second = TaggedText().complete(self.contents, 'span class="List-contents"')
    self.contents = [first, second]

class PlainLayout(Layout):
  "A plain layout"

  def process(self):
    "Output just as contents."
    self.output = ContentsOutput()
    self.type = 'Plain'

  def makevisible(self):
    "Make the layout visible, output as tagged text."
    self.output = TaggedOutput().settag('div class="PlainVisible"', True)

class LyXCode(Layout):
  "A bit of LyX-Code."

  def process(self):
    "Output as pre."
    self.output.tag = 'pre class="LyX-Code"'
    for newline in self.searchall(Newline):
      index = newline.parent.contents.index(newline)
      newline.parent.contents[index] = Constant('\n')

class PostLayout(object):
  "Numerate an indexed layout"

  processedclass = Layout

  def postprocess(self, last, layout, next):
    "Generate a number and place it before the text"
    if not hasattr(layout, 'number'):
      return layout
    label = Label().create(layout.anchortext, layout.partkey, type='toc')
    layout.contents.insert(0, label)
    if layout.anchortext != '':
      layout.contents.insert(1, Constant(u' '))
    return layout

  def modifylayout(self, layout, type):
    "Modify a layout according to the given type."
    layout.level = NumberGenerator.instance.getlevel(type)
    layout.output.tag = layout.output.tag.replace('?', unicode(layout.level))

  def containsappendix(self, layout):
    "Find out if there is an appendix somewhere in the layout"
    for element in layout.contents:
      if isinstance(element, Appendix):
        return True
    return False

  def activateappendix(self):
    "Change first number to letter, and chapter to appendix"
    NumberGenerator.instance.number = ['-']

class PostStandard(object):
  "Convert any standard spans in root to divs"

  processedclass = StandardLayout

  def postprocess(self, last, standard, next):
    "Switch to div"
    type = 'Standard'
    if LyXHeader.indentstandard:
      if isinstance(last, StandardLayout):
        type = 'Indented'
      else:
        type = 'Unindented'
    standard.output = TaggedOutput().settag('div class="' + type + '"', True)
    return standard

class PostLyXCode(object):
  "Coalesce contiguous LyX-Code layouts."

  processedclass = LyXCode

  def postprocess(self, last, lyxcode, next):
    "Coalesce if last was also LyXCode"
    if not isinstance(last, LyXCode):
      return lyxcode
    if hasattr(last, 'first'):
      lyxcode.first = last.first
    else:
      lyxcode.first = last
    toappend = lyxcode.first.contents
    toappend.append(Constant('\n'))
    toappend += lyxcode.contents
    lyxcode.output = EmptyOutput()
    return lyxcode

Postprocessor.stages += [PostLayout, PostStandard, PostLyXCode]



class BiblioCitation(Container):
  "A complete bibliography citation (possibly with many cites)."

  citations = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('sup')
    self.contents = []

  def process(self):
    "Process the complete citation and all cites within."
    keys = self.parameters['key'].split(',')
    for key in keys:
      self.contents += [BiblioCite().create(key), Constant(',')]
    if len(keys) > 0:
      # remove trailing ,
      self.contents.pop()

class BiblioCite(Link):
  "Cite of a bibliography entry"

  cites = dict()

  def create(self, key):
    "Create the cite to the given key."
    self.key = key
    number = NumberGenerator.instance.generateunique('bibliocite')
    ref = BiblioReference().create(key, number)
    self.complete(number, 'cite-' + number, type='bibliocite')
    self.setmutualdestination(ref)
    if not key in BiblioCite.cites:
      BiblioCite.cites[key] = []
    BiblioCite.cites[key].append(self)
    return self

class Bibliography(Container):
  "A bibliography layout containing an entry"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = TaggedOutput().settag('p class="biblio"', True)

class PostBiblio(object):
  "Insert a Bibliography legend before the first item"

  processedclass = Bibliography

  def postprocess(self, last, element, next):
    "If we have the first bibliography insert a tag"
    if isinstance(last, Bibliography) or Options.nobib:
      return element
    bibliography = Translator.translate('bibliography')
    header = TaggedText().constant(bibliography, 'h1 class="biblio"')
    layout = StandardLayout().complete([header, element])
    return layout

Postprocessor.stages += [PostBiblio]

class BiblioReference(Link):
  "A reference to a bibliographical entry."

  references = dict()

  def create(self, key, number):
    "Create the reference with the given key and number."
    self.key = key
    self.complete(number, 'biblio-' + number, type='biblioentry')
    if not key in BiblioReference.references:
      BiblioReference.references[key] = []
    BiblioReference.references[key].append(self)
    return self

class BiblioEntry(Container):
  "A bibliography entry"

  entries = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="entry"')

  def process(self):
    "Process the cites for the entry's key"
    self.processcites(self.parameters['key'])

  def processcites(self, key):
    "Get all the cites of the entry"
    self.key = key
    if not key in BiblioReference.references:
      self.contents.append(Constant('[-] '))
      return
    self.contents = [Constant('[')]
    for ref in BiblioReference.references[key]:
      self.contents.append(ref)
      self.contents.append(Constant(','))
    self.contents.pop(-1)
    self.contents.append(Constant('] '))




import sys





class Cloner(object):
  "An object used to clone other objects."

  clonelist = ['contents']

  def clone(cls, original):
    "Return an exact copy of an object."
    "The original object must have an empty constructor."
    type = original.__class__
    clone = type.__new__(type)
    clone.__init__()
    return clone

  clone = classmethod(clone)




import sys


class FormulaParser(Parser):
  "Parses a formula"

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    if reader.currentline().find(FormulaConfig.starts['simple']) > 0:
      return ['inline']
    if reader.currentline().find(FormulaConfig.starts['complex']) > 0:
      return ['block']
    if reader.currentline().find(FormulaConfig.starts['unnumbered']) > 0:
      return ['block']
    return ['numbered']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parseformula(reader)
    while not reader.currentline().startswith(self.ending):
      stripped = reader.currentline().strip()
      if len(stripped) > 0:
        Trace.error('Unparsed formula line ' + stripped)
      reader.nextline()
    reader.nextline()
    return [formula]

  def parseformula(self, reader):
    "Parse the formula contents"
    simple = FormulaConfig.starts['simple']
    if simple in reader.currentline():
      rest = reader.currentline().split(simple, 1)[1]
      if simple in rest:
        # formula is $...$
        return self.parsesingleliner(reader, simple, simple)
      # formula is multiline $...$
      return self.parsemultiliner(reader, simple, simple)
    if FormulaConfig.starts['complex'] in reader.currentline():
      # formula of the form \[...\]
      return self.parsemultiliner(reader, FormulaConfig.starts['complex'],
          FormulaConfig.endings['complex'])
    beginbefore = FormulaConfig.starts['beginbefore']
    beginafter = FormulaConfig.starts['beginafter']
    if beginbefore in reader.currentline():
      if reader.currentline().strip().endswith(beginafter):
        current = reader.currentline().strip()
        endsplit = current.split(beginbefore)[1].split(beginafter)
        startpiece = beginbefore + endsplit[0] + beginafter
        endbefore = FormulaConfig.endings['endbefore']
        endafter = FormulaConfig.endings['endafter']
        endpiece = endbefore + endsplit[0] + endafter
        return startpiece + self.parsemultiliner(reader, startpiece, endpiece) + endpiece
      Trace.error('Missing ' + beginafter + ' in ' + reader.currentline())
      return ''
    begincommand = FormulaConfig.starts['command']
    beginbracket = FormulaConfig.starts['bracket']
    if begincommand in reader.currentline() and beginbracket in reader.currentline():
      endbracket = FormulaConfig.endings['bracket']
      return self.parsemultiliner(reader, beginbracket, endbracket)
    Trace.error('Formula beginning ' + reader.currentline() + ' is unknown')
    return ''

  def parsesingleliner(self, reader, start, ending):
    "Parse a formula in one line"
    line = reader.currentline().strip()
    if not start in line:
      Trace.error('Line ' + line + ' does not contain formula start ' + start)
      return ''
    if not line.endswith(ending):
      Trace.error('Formula ' + line + ' does not end with ' + ending)
      return ''
    index = line.index(start)
    rest = line[index + len(start):-len(ending)]
    reader.nextline()
    return rest

  def parsemultiliner(self, reader, start, ending):
    "Parse a formula in multiple lines"
    formula = ''
    line = reader.currentline()
    if not start in line:
      Trace.error('Line ' + line.strip() + ' does not contain formula start ' + start)
      return ''
    index = line.index(start)
    line = line[index + len(start):].strip()
    while not line.endswith(ending):
      formula += line
      reader.nextline()
      line = reader.currentline()
    formula += line[:-len(ending)]
    reader.nextline()
    return formula

class MacroParser(FormulaParser):
  "A parser for a formula macro."

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    return ['inline']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parsemultiliner(reader, self.parent.start, self.ending)
    reader.nextline()
    return [formula]
  


class Formula(Container):
  "A LaTeX formula"

  initializations = []

  def __init__(self):
    self.parser = FormulaParser()
    self.output = TaggedOutput().settag('span class="formula"')
    self.initialize()

  def process(self):
    "Convert the formula to tags"
    if self.header[0] != 'inline':
      self.output.settag('div class="formula"', True)
    if Options.jsmath:
      if self.header[0] != 'inline':
        self.output = TaggedOutput().settag('div class="math"')
      else:
        self.output = TaggedOutput().settag('span class="math"')
      self.contents = [Constant(self.contents[0])]
      return
    if Options.mathjax:
      self.output.tag = 'span class="MathJax_Preview"'
      tag = 'script type="math/tex'
      if self.header[0] != 'inline':
        tag += ';mode=display'
      self.contents = [TaggedText().constant(self.contents[0], tag + '"', True)]
      return
    whole = WholeFormula.parse(self.contents[0])
    self.contents = [whole]
    whole.parent = self

  def initialize(self):
    "Perform any necessary initializations."
    "Introduced to process any macros in the preamble."
    for init in Formula.initializations:
      init()

  def __unicode__(self):
    "Return a printable representation."
    if hasattr(self, 'number'):
      return 'Formula (' + self.number + ')'
    return 'Unnumbered formula'

class FormulaBit(Container):
  "A bit of a formula"

  def __init__(self):
    # type can be 'alpha', 'number', 'font'
    self.type = None
    self.original = ''
    self.contents = []
    self.output = ContentsOutput()

  def add(self, bit):
    "Add any kind of formula bit already processed"
    self.contents.append(bit)
    self.original += bit.original
    bit.parent = self

  def skiporiginal(self, string, pos):
    "Skip a string and add it to the original formula"
    self.original += string
    if not pos.checkskip(string):
      Trace.error('String ' + string + ' not at ' + pos.identifier())

  def clone(self):
    "Return a copy of itself."
    return WholeFormula.parse(self.original)

  def __unicode__(self):
    "Get a string representation"
    return self.__class__.__name__ + ' read in ' + self.original

class TaggedBit(FormulaBit):
  "A tagged string in a formula"

  def constant(self, constant, tag):
    "Set the constant and the tag"
    self.output = TaggedOutput().settag(tag)
    self.add(FormulaConstant(constant))
    return self

  def complete(self, contents, tag):
    "Set the constant and the tag"
    self.contents = contents
    self.output = TaggedOutput().settag(tag)
    return self

class FormulaConstant(Constant):
  "A constant string in a formula"

  def __init__(self, string):
    "Set the constant string"
    Constant.__init__(self, string)
    self.original = string
    self.type = None

class WholeFormula(FormulaBit):
  "Parse a whole formula"

  def __init__(self):
    FormulaBit.__init__(self)
    self.factory = FormulaFactory()

  def detect(self, pos):
    "Check in the factory"
    return self.factory.detectbit(pos)

  def parsebit(self, pos):
    "Parse with any formula bit"
    while self.factory.detectbit(pos):
      bit = self.factory.parsebit(pos)
      #Trace.debug(bit.original + ' -> ' + unicode(bit.gethtml()))
      self.add(bit)

  def process(self):
    "Process the whole formula"
    for index, bit in enumerate(self.contents):
      bit.process()
      # no units processing
      continue
      if bit.type == 'alpha':
        # make variable
        self.contents[index] = TaggedBit().complete([bit], 'i')
      elif bit.type == 'font' and index > 0:
        last = self.contents[index - 1]
        if last.type == 'number':
          #separate
          last.contents.append(FormulaConstant(u' '))

  def parse(cls, formula):
    "Parse a whole formula and return it."
    pos = TextPosition(formula)
    whole = WholeFormula()
    if not whole.detect(pos):
      Trace.error('Unknown formula at: ' + pos.identifier())
      return TaggedBit().constant(pos.identifier(), 'span class="unknown"')
    whole.parsebit(pos)
    whole.process()
    return whole

  parse = classmethod(parse)

class FormulaFactory(object):
  "Construct bits of formula"

  # bits will be appended later
  bits = []

  def detectbit(self, pos):
    "Detect if there is a next bit"
    if pos.finished():
      return False
    for bit in FormulaFactory.bits:
      if bit.detect(pos):
        return True
    return False

  def parsebit(self, pos):
    "Parse just one formula bit."
    for bit in FormulaFactory.bits:
      if bit.detect(pos):
        # get a fresh bit and parse it
        newbit = Cloner.clone(bit)
        newbit.factory = self
        returnedbit = newbit.parsebit(pos)
        if returnedbit:
          return returnedbit
        return newbit
    Trace.error('Unrecognized formula at ' + pos.identifier())
    return FormulaConstant(pos.currentskip())




import sys



import sys


class RawText(FormulaBit):
  "A bit of text inside a formula"

  def detect(self, pos):
    "Detect a bit of raw text"
    return pos.current().isalpha()

  def parsebit(self, pos):
    "Parse alphabetic text"
    alpha = pos.globalpha()
    self.add(FormulaConstant(alpha))
    self.type = 'alpha'

class FormulaSymbol(FormulaBit):
  "A symbol inside a formula"

  modified = FormulaConfig.modified
  unmodified = FormulaConfig.unmodified['characters']

  def detect(self, pos):
    "Detect a symbol"
    if pos.current() in FormulaSymbol.unmodified:
      return True
    if pos.current() in FormulaSymbol.modified:
      return True
    return False

  def parsebit(self, pos):
    "Parse the symbol"
    if pos.current() in FormulaSymbol.unmodified:
      self.addsymbol(pos.current(), pos)
      return
    if pos.current() in FormulaSymbol.modified:
      self.addsymbol(FormulaSymbol.modified[pos.current()], pos)
      return
    Trace.error('Symbol ' + pos.current() + ' not found')

  def addsymbol(self, symbol, pos):
    "Add a symbol"
    self.skiporiginal(pos.current(), pos)
    self.contents.append(FormulaConstant(symbol))

class Number(FormulaBit):
  "A string of digits in a formula"

  def detect(self, pos):
    "Detect a digit"
    return pos.current().isdigit()

  def parsebit(self, pos):
    "Parse a bunch of digits"
    digits = pos.glob(lambda current: current.isdigit())
    self.add(FormulaConstant(digits))
    self.type = 'number'

class Comment(FormulaBit):
  "A LaTeX comment: % to the end of the line."

  def detect(self, pos):
    "Detect the %."
    return pos.current() == '%'

  def parsebit(self, pos):
    "Parse to the end of the line."
    comment = pos.globincluding('\n')
    self.original += comment

class Bracket(FormulaBit):
  "A {} bracket inside a formula"

  start = FormulaConfig.starts['bracket']
  ending = FormulaConfig.endings['bracket']

  def __init__(self):
    "Create a (possibly literal) new bracket"
    FormulaBit.__init__(self)
    self.inner = None

  def detect(self, pos):
    "Detect the start of a bracket"
    return pos.checkfor(self.start)

  def parsebit(self, pos):
    "Parse the bracket"
    self.parsecomplete(pos, self.innerformula)
    return self

  def parsetext(self, pos):
    "Parse a text bracket"
    self.parsecomplete(pos, self.innertext)
    return self

  def parseliteral(self, pos):
    "Parse a literal bracket"
    self.parsecomplete(pos, self.innerliteral)
    return self

  def parsecomplete(self, pos, innerparser):
    "Parse the start and end marks"
    if not pos.checkfor(self.start):
      Trace.error('Bracket should start with ' + self.start + ' at ' + pos.identifier())
      return None
    self.skiporiginal(self.start, pos)
    pos.pushending(self.ending)
    innerparser(pos)
    self.original += pos.popending(self.ending)

  def innerformula(self, pos):
    "Parse a whole formula inside the bracket"
    self.inner = WholeFormula()
    if self.inner.detect(pos):
      self.inner.parsebit(pos)
      self.add(self.inner)
      return
    if pos.finished():
      return
    if pos.current() != self.ending:
      Trace.error('No formula in bracket at ' + pos.identifier())
    return

  def innertext(self, pos):
    "Parse some text inside the bracket, following textual rules."
    factory = FormulaFactory()
    while not pos.finished():
      if pos.current() == FormulaConfig.starts['command'] or \
          pos.current() in FormulaConfig.symbolfunctions:
        bit = factory.parsebit(pos)
        pos.checkskip(' ')
      else:
        bit = FormulaConstant(pos.currentskip())
      self.add(bit)

  def innerliteral(self, pos):
    "Parse a literal inside the bracket, which cannot generate html"
    self.literal = ''
    while not pos.current() == self.ending:
      if pos.current() == self.start:
        self.parseliteral(pos)
      else:
        self.literal += pos.currentskip()
    self.original += self.literal

  def process(self):
    "Process the bracket"
    if self.inner:
      self.inner.process()

class SquareBracket(Bracket):
  "A [] bracket inside a formula"

  start = FormulaConfig.starts['squarebracket']
  ending = FormulaConfig.endings['squarebracket']

FormulaFactory.bits += [
    FormulaSymbol(), RawText(), Number(), Comment(), Bracket()
    ]



class FormulaCommand(FormulaBit):
  "A LaTeX command inside a formula"

  commandbits = []
  start = FormulaConfig.starts['command']
  preambling = False

  def detect(self, pos):
    "Find the current command"
    return pos.checkfor(FormulaCommand.start)

  def parsebit(self, pos):
    "Parse the command"
    command = self.extractcommand(pos)
    for bit in FormulaCommand.commandbits:
      if bit.recognize(command):
        newbit = Cloner.clone(bit)
        newbit.factory = self.factory
        newbit.setcommand(command)
        newbit.parsebit(pos)
        self.add(newbit)
        return newbit
    if not self.preambling:
      Trace.error('Unknown command ' + command)
    self.output = TaggedOutput().settag('span class="unknown"')
    self.add(FormulaConstant(command))
    return None

  def extractcommand(self, pos):
    "Extract the command from the current position"
    if not pos.checkskip(FormulaCommand.start):
      Trace.error('Missing command start ' + start)
      return
    if pos.current().isalpha():
      # alpha command
      return FormulaCommand.start + pos.globalpha()
    # symbol command
    return FormulaCommand.start + pos.currentskip()

  def process(self):
    "Process the internals"
    for bit in self.contents:
      bit.process()

class CommandBit(FormulaCommand):
  "A formula bit that includes a command"

  def recognize(self, command):
    "Recognize the command as own"
    return command in self.commandmap

  def setcommand(self, command):
    "Set the command in the bit"
    self.command = command
    self.original += command
    self.translated = self.commandmap[self.command]
 
  def parseparameter(self, pos):
    "Parse a parameter at the current position"
    if not self.factory.detectbit(pos):
      Trace.error('No parameter found at: ' + pos.identifier())
      return None
    parameter = self.factory.parsebit(pos)
    self.add(parameter)
    return parameter

  def parsesquare(self, pos):
    "Parse a square bracket"
    bracket = SquareBracket()
    if not bracket.detect(pos):
      return None
    bracket.parsebit(pos)
    self.add(bracket)
    return bracket

  def parseliteral(self, pos):
    "Parse a literal bracket."
    bracket = Bracket()
    if not bracket.detect(pos):
      Trace.error('No literal parameter found at: ' + pos.identifier())
      return None
    self.add(bracket.parseliteral(pos))
    return bracket.literal

  def parsesquareliteral(self, pos):
    "Parse a square bracket literally."
    bracket = SquareBracket()
    if not bracket.detect(pos):
      return None
    self.add(bracket.parseliteral(pos))
    return bracket.literal

class EmptyCommand(CommandBit):
  "An empty command (without parameters)"

  commandmap = FormulaConfig.commands

  def parsebit(self, pos):
    "Parse a command without parameters"
    self.contents = [FormulaConstant(self.translated)]

class AlphaCommand(EmptyCommand):
  "A command without paramters whose result is alphabetical"

  commandmap = FormulaConfig.alphacommands

  def parsebit(self, pos):
    "Parse the command and set type to alpha"
    EmptyCommand.parsebit(self, pos)
    self.type = 'alpha'

class OneParamFunction(CommandBit):
  "A function of one parameter"

  commandmap = FormulaConfig.onefunctions

  def parsebit(self, pos):
    "Parse a function with one parameter"
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)
    self.simplifyifpossible()

  def simplifyifpossible(self):
    "Try to simplify to a single character."
    if self.original in self.commandmap:
      self.output = FixedOutput()
      self.html = [self.commandmap[self.original]]

class SymbolFunction(CommandBit):
  "Find a function which is represented by a symbol (like _ or ^)"

  commandmap = FormulaConfig.symbolfunctions

  def detect(self, pos):
    "Find the symbol"
    return pos.current() in SymbolFunction.commandmap

  def parsebit(self, pos):
    "Parse the symbol"
    self.setcommand(pos.current())
    pos.skip(self.command)
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)

class TextFunction(CommandBit):
  "A function where parameters are read as text."

  commandmap = FormulaConfig.textfunctions

  def parsebit(self, pos):
    "Parse a text parameter"
    self.output = TaggedOutput().settag(self.translated)
    bracket = Bracket().parsetext(pos)
    self.add(bracket)

  def process(self):
    "Set the type to font"
    self.type = 'font'

class LabelFunction(CommandBit):
  "A function that acts as a label"

  commandmap = FormulaConfig.labelfunctions

  def parsebit(self, pos):
    "Parse a literal parameter"
    self.key = self.parseliteral(pos)

  def process(self):
    "Add an anchor with the label contents."
    self.type = 'font'
    self.label = Label().create(' ', self.key, type = 'eqnumber')
    self.contents = [self.label]
    # store as a Label so we know it's been seen
    Label.names[self.key] = self.label

class FontFunction(OneParamFunction):
  "A function of one parameter that changes the font"

  commandmap = FormulaConfig.fontfunctions

  def process(self):
    "Simplify if possible using a single character."
    self.type = 'font'
    self.simplifyifpossible()

class DecoratingFunction(OneParamFunction):
  "A function that decorates some bit of text"

  commandmap = FormulaConfig.decoratingfunctions

  def parsebit(self, pos):
    "Parse a decorating function"
    self.output = TaggedOutput().settag('span class="withsymbol"')
    self.type = 'alpha'
    symbol = self.translated
    self.symbol = TaggedBit().constant(symbol, 'span class="symbolover"')
    self.contents.append(self.symbol)
    self.parameter = self.parseparameter(pos)
    self.parameter.output = TaggedOutput().settag('span class="undersymbol"')
    self.simplifyifpossible()

class UnderDecoratingFunction(DecoratingFunction):
  "A function that decorates some bit of text from below."

  commandmap = FormulaConfig.underdecoratingfunctions

  def parsebit(self, pos):
    "Parse an under-decorating function."
    DecoratingFunction.parsebit(self, pos)
    self.symbol.output.settag('span class="symbolunder"')
    self.parameter.output.settag('span class="oversymbol"')

FormulaFactory.bits += [FormulaCommand(), SymbolFunction()]
FormulaCommand.commandbits = [
    EmptyCommand(), AlphaCommand(), OneParamFunction(), DecoratingFunction(),
    FontFunction(), LabelFunction(), TextFunction(), UnderDecoratingFunction(),
    ]




import sys


class ParameterDefinition(object):
  "The definition of a parameter in a hybrid function."
  "[] parameters are optional, {} parameters are mandatory."
  "Each parameter has a one-character name, like {$1} or {$p}."
  "A parameter that ends in ! like {$p!} is a literal."

  parambrackets = [('[', ']'), ('{', '}')]

  def __init__(self):
    self.name = None
    self.literal = False
    self.optional = False
    self.value = None
    self.literalvalue = None

  def parse(self, pos):
    "Parse a parameter definition: [$0], {$x}, {$1!}..."
    for (opening, closing) in ParameterDefinition.parambrackets:
      if pos.checkskip(opening):
        if opening == '[':
          self.optional = True
        if not pos.checkskip('$'):
          Trace.error('Wrong parameter name ' + pos.current())
          return None
        self.name = pos.currentskip()
        if pos.checkskip('!'):
          self.literal = True
        if not pos.checkskip(closing):
          Trace.error('Wrong parameter closing ' + pos.currentskip())
          return None
        return self
    Trace.error('Wrong character in parameter template' + pos.currentskip())
    return None

  def read(self, pos, function):
    "Read the parameter itself using the definition."
    if self.literal:
      if self.optional:
        self.literalvalue = function.parsesquareliteral(pos)
      else:
        self.literalvalue = function.parseliteral(pos)
      if self.literalvalue:
        self.value = FormulaConstant(self.literalvalue)
    elif self.optional:
      self.value = function.parsesquare(pos)
    else:
      self.value = function.parseparameter(pos)

  def __unicode__(self):
    "Return a printable representation."
    result = 'param ' + self.name
    if self.value:
      result += ': ' + unicode(self.value)
    else:
      result += ' (empty)'
    return result

class HybridFunction(CommandBit):
  "Read a function with a variable number of parameters, defined in a template."

  commandmap = FormulaConfig.hybridfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters"
    readtemplate = self.translated[0]
    writetemplate = self.translated[1]
    self.readparams(readtemplate, pos)
    self.contents = self.writeparams(writetemplate)

  def readparams(self, readtemplate, pos):
    "Read the params according to the template."
    self.params = dict()
    for paramdef in self.paramdefs(readtemplate):
      paramdef.read(pos, self)
      self.params['$' + paramdef.name] = paramdef

  def paramdefs(self, readtemplate):
    "Read each param definition in the template"
    pos = TextPosition(readtemplate)
    while not pos.finished():
      paramdef = ParameterDefinition().parse(pos)
      if paramdef:
        yield paramdef

  def writeparams(self, writetemplate):
    "Write all params according to the template"
    return self.writepos(TextPosition(writetemplate))

  def writepos(self, pos):
    "Write all params as read in the parse position."
    result = []
    while not pos.finished():
      if pos.checkskip('$'):
        param = self.writeparam(pos)
        if param:
          result.append(param)
      elif pos.checkskip('f'):
        function = self.writefunction(pos)
        if function:
          result.append(function)
      else:
        result.append(FormulaConstant(pos.currentskip()))
    return result

  def writeparam(self, pos):
    "Write a single param of the form $0, $x..."
    name = '$' + pos.currentskip()
    if not name in self.params:
      Trace.error('Unknown parameter ' + name)
      return None
    if not self.params[name]:
      return None
    if pos.checkskip('.'):
      self.params[name].value.type = pos.globalpha()
    return self.params[name].value

  def writefunction(self, pos):
    "Write a single function f0,...,fn."
    tag = self.readtag(pos)
    if not tag:
      return None
    if not pos.checkskip('{'):
      Trace.error('Function should be defined in {}')
      return None
    pos.pushending('}')
    contents = self.writepos(pos)
    pos.popending()
    if len(contents) == 0:
      return None
    function = TaggedBit().complete(contents, tag)
    function.type = None
    return function

  def readtag(self, pos):
    "Get the tag corresponding to the given index. Does parameter substitution."
    if not pos.current().isdigit():
      Trace.error('Function should be f0,...,f9: f' + pos.current())
      return None
    index = int(pos.currentskip())
    if 2 + index > len(self.translated):
      Trace.error('Function f' + unicode(index) + ' is not defined')
      return None
    tag = self.translated[2 + index]
    if not '$' in tag:
      return tag
    for variable in self.params:
      if variable in tag:
        param = self.params[variable]
        if not param.literal:
          Trace.error('Parameters in tag ' + tag + ' should be literal: {' + variable + '!}')
          continue
        if param.literalvalue:
          value = param.literalvalue
        else:
          value = ''
        tag = tag.replace(variable, value)
    return tag

FormulaCommand.commandbits += [
    HybridFunction(),
    ]









class TableParser(BoundedParser):
  "Parse the whole table"

  headers = ContainerConfig.table['headers']

  def __init__(self):
    BoundedParser.__init__(self)
    self.columns = list()

  def parseheader(self, reader):
    "Parse table headers"
    reader.nextline()
    while self.startswithheader(reader):
      self.parseparameter(reader)
    return []

  def startswithheader(self, reader):
    "Check if the current line starts with a header line"
    for start in TableParser.headers:
      if reader.currentline().strip().startswith(start):
        return True
    return False

class TablePartParser(BoundedParser):
  "Parse a table part (row or cell)"

  def parseheader(self, reader):
    "Parse the header"
    tablekey, parameters = self.parsexml(reader)
    self.parameters = parameters
    return list()

class ColumnParser(LoneCommand):
  "Parse column properties"

  def parseheader(self, reader):
    "Parse the column definition"
    key, parameters = self.parsexml(reader)
    self.parameters = parameters
    return []



class Table(Container):
  "A lyx table"

  def __init__(self):
    self.parser = TableParser()
    self.output = TaggedOutput().settag('table', True)
    self.columns = []

  def process(self):
    "Set the columns on every row"
    index = 0
    while index < len(self.contents):
      element = self.contents[index]
      if isinstance(element, Column):
        self.columns.append(element)
        del self.contents[index]
      elif isinstance(element, BlackBox):
        del self.contents[index]
      elif isinstance(element, Row):
        element.setcolumns(self.columns)
        index += 1
      else:
        Trace.error('Unknown element type ' + element.__class__.__name__ +
            ' in table: ' + unicode(element.contents[0]))
        index += 1

class Row(Container):
  "A row in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('tr', True)
    self.columns = list()

  def setcolumns(self, columns):
    "Process alignments for every column"
    if len(columns) != len(self.contents):
      Trace.error('Columns: ' + unicode(len(columns)) + ', cells: ' + unicode(len(self.contents)))
      return
    for index, cell in enumerate(self.contents):
      columns[index].set(cell)

class Column(Container):
  "A column definition in a table"

  def __init__(self):
    self.parser = ColumnParser()
    self.output = EmptyOutput()

  def set(self, cell):
    "Set alignments in the corresponding cell"
    alignment = self.parameters['alignment']
    if alignment == 'block':
      alignment = 'justify'
    cell.setattribute('align', alignment)
    valignment = self.parameters['valignment']
    cell.setattribute('valign', valignment)

class Cell(Container):
  "A cell in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('td', True)

  def setmulticolumn(self, span):
    "Set the cell as multicolumn"
    self.setattribute('colspan', span)

  def setattribute(self, attribute, value):
    "Set a cell attribute in the tag"
    self.output.tag += ' ' + attribute + '="' + unicode(value) + '"'




import struct
import sys
import os



import os
import os.path
import codecs


class Path(object):
  "Represents a generic path"

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def open(self):
    "Open the file as readonly binary"
    return codecs.open(self.path, 'rb')

  def getmtime(self):
    "Return last modification time"
    return os.path.getmtime(self.path)

  def hasexts(self, exts):
    "Check if the file has one of the given extensions."
    for ext in exts:
      if self.hasext(ext):
        return True
    return False

  def hasext(self, ext):
    "Check if the file has the given extension"
    base, oldext = os.path.splitext(self.path)
    return oldext == ext

  def __unicode__(self):
    "Return a unicode string representation"
    return self.path

  def __eq__(self, path):
    "Compare to another path"
    if not hasattr(path, 'path'):
      return False
    return self.path == path.path

class InputPath(Path):
  "Represents an input file"

  def __init__(self, url):
    "Create the input path based on url"
    self.url = url
    self.path = url
    if not os.path.isabs(url):
      self.path = os.path.join(Options.directory, url)

class OutputPath(Path):
  "Represents an output file"

  def __init__(self, inputpath):
    "Create the output path based on an input path"
    self.url = inputpath.url
    if os.path.isabs(self.url):
      self.url = os.path.basename(self.url)
    self.path = os.path.join(Options.destdirectory, self.url)
  
  def changeext(self, ext):
    "Change extension to the given one"
    base, oldext = os.path.splitext(self.path)
    self.path = base + ext
    base, oldext = os.path.splitext(self.url)
    self.url = base + ext

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def createdirs(self):
    "Create any intermediate directories that don't exist"
    dir = os.path.dirname(self.path)
    if len(dir) > 0 and not os.path.exists(dir):
      os.makedirs(dir)

  def removebackdirs(self):
    "Remove any occurrences of ../ (or ..\ on Windows)"
    self.path = os.path.normpath(self.path)
    backdir = '..' + os.path.sep
    while self.path.startswith(backdir):
      Trace.debug('Backdir in: ' + self.path)
      self.path = self.path[len(backdir):]
    while self.url.startswith('../'):
      Trace.debug('Backdir in: ' + self.url)
      self.url = self.url[len('../'):]



class Image(Container):
  "An embedded image"

  ignoredtexts = ImageConfig.size['ignoredtexts']
  vectorformats = ImageConfig.formats['vector']
  rasterformats = ImageConfig.formats['raster']
  defaultformat = ImageConfig.formats['default']

  def __init__(self):
    self.parser = InsetParser()
    self.output = ImageOutput()
    self.type = 'embedded'
    self.width = None
    self.height = None
    self.maxwidth = None
    self.maxheight = None
    self.scale = None

  def process(self):
    "Place the url, convert the image if necessary."
    self.origin = InputPath(self.parameters['filename'])
    if not self.origin.exists():
      Trace.error('Image ' + unicode(self.origin) + ' not found')
      return
    self.destination = self.getdestination(self.origin)
    self.setscale()
    ImageConverter.instance.convert(self)
    self.setsize()

  def getdestination(self, origin):
    "Convert origin path to destination path."
    "Changes extension of destination to output image format."
    destination = OutputPath(origin)
    forceformat = '.jpg'
    forcedest = Image.defaultformat
    if Options.forceformat:
      forceformat = Options.forceformat
      forcedest = Options.forceformat
    if not destination.hasext(forceformat):
      destination.changeext(forcedest)
    destination.removebackdirs()
    return destination

  def setscale(self):
    "Set the scale attribute if present."
    self.setifparam('scale')

  def setsize(self):
    "Set the size attributes width and height."
    imagefile = ImageFile(self.destination)
    width, height = imagefile.getdimensions()
    if width:
      self.maxwidth = unicode(width) + 'px'
      if self.scale:
        self.width = self.scalevalue(width)
    if height:
      self.maxheight = unicode(height) + 'px'
      if self.scale:
        self.height = self.scalevalue(height)
    self.setifparam('width')
    self.setifparam('height')

  def setifparam(self, name):
    "Set the value in the container if it exists as a param."
    if not name in self.parameters:
      return
    value = unicode(self.parameters[name])
    for ignored in Image.ignoredtexts:
      if ignored in value:
        value = value.replace(ignored, '')
    setattr(self, name, value)

  def scalevalue(self, value):
    "Scale the value according to the image scale and return it as unicode."
    scaled = value * int(self.scale) / 100
    return unicode(int(scaled)) + 'px'

class ImageConverter(object):
  "A converter from one image file to another."

  active = True
  instance = None

  def convert(self, image):
    "Convert an image to PNG"
    if not ImageConverter.active:
      return
    if image.origin.path == image.destination.path:
      return
    if image.destination.exists():
      if image.origin.getmtime() <= image.destination.getmtime():
        # file has not changed; do not convert
        return
    image.destination.createdirs()
    converter, command = self.buildcommand(image)
    try:
      Trace.debug(converter + ' command: "' + command + '"')
      result = os.system(command.encode(sys.getfilesystemencoding()))
      if result != 0:
        Trace.error(converter + ' not installed; images will not be processed')
        ImageConverter.active = False
        return
      Trace.message('Converted ' + unicode(image.origin) + ' to ' +
          unicode(image.destination))
    except OSError, exception:
      Trace.error('Error while converting image ' + unicode(image.origin)
          + ': ' + unicode(exception))

  def buildcommand(self, image):
    "Build the command to convert the image."
    if not Options.converter in ImageConfig.converters:
      Trace.error('Converter ' + Options.converter + ' not configured.')
      ImageConverter.active = False
      return ''
    command = ImageConfig.converters[Options.converter]
    params = self.getparams(image)
    for param in params:
      command = command.replace('$' + param, unicode(params[param]))
    # remove unwanted options
    while '[' in command and ']' in command:
      command = self.removeparam(command)
    return Options.converter, command

  def removeparam(self, command):
    "Remove an unwanted param."
    if command.index('[') > command.index(']'):
      Trace.error('Converter command should be [...$...]: ' + command)
      exit()
    before = command[:command.index('[')]
    after = command[command.index(']') + 1:]
    between = command[command.index('[') + 1:command.index(']')]
    if '$' in between:
      return before + after
    return before + between + after

  def getparams(self, image):
    "Get the parameters for ImageMagick conversion"
    params = dict()
    params['input'] = image.origin
    params['output'] = image.destination
    if image.origin.hasexts(Image.vectorformats):
      scale = 100
      if image.scale:
        scale = image.scale
        # descale
        image.scale = None
      params['scale'] = scale
    # elif image.origin.hasext('.pdf'):
      # params['define'] = 'pdf:use-cropbox=true'
    return params

ImageConverter.instance = ImageConverter()

class ImageFile(object):
  "A file corresponding to an image (JPG or PNG)"

  dimensions = dict()

  def __init__(self, path):
    "Create the file based on its path"
    self.path = path

  def getdimensions(self):
    "Get the dimensions of a JPG or PNG image"
    if not self.path.exists():
      return None, None
    if unicode(self.path) in ImageFile.dimensions:
      return ImageFile.dimensions[unicode(self.path)]
    dimensions = (None, None)
    if self.path.hasext('.png'):
      dimensions = self.getpngdimensions()
    elif self.path.hasext('.jpg'):
      dimensions = self.getjpgdimensions()
    ImageFile.dimensions[unicode(self.path)] = dimensions
    return dimensions

  def getpngdimensions(self):
    "Get the dimensions of a PNG image"
    pngfile = self.path.open()
    pngfile.seek(16)
    width = self.readlong(pngfile)
    height = self.readlong(pngfile)
    pngfile.close()
    return (width, height)

  def getjpgdimensions(self):
    "Get the dimensions of a JPEG image"
    jpgfile = self.path.open()
    start = self.readword(jpgfile)
    if start != int('ffd8', 16):
      Trace.error(unicode(self.path) + ' not a JPEG file')
      return (None, None)
    self.skipheaders(jpgfile, ['ffc0', 'ffc2'])
    self.seek(jpgfile, 3)
    height = self.readword(jpgfile)
    width = self.readword(jpgfile)
    jpgfile.close()
    return (width, height)

  def skipheaders(self, file, hexvalues):
    "Skip JPEG headers until one of the parameter headers is found"
    headervalues = [int(value, 16) for value in hexvalues]
    header = self.readword(file)
    safetycounter = 0
    while header not in headervalues and safetycounter < 30:
      length = self.readword(file)
      if length == 0:
        Trace.error('End of file ' + file.name)
        return
      self.seek(file, length - 2)
      header = self.readword(file)
      safetycounter += 1

  def readlong(self, file):
    "Read a long (32-bit) value from file"
    return self.readformat(file, '>L', 4)

  def readword(self, file):
    "Read a 16-bit value from file"
    return self.readformat(file, '>H', 2)

  def readformat(self, file, format, bytes):
    "Read any format from file"
    read = file.read(bytes)
    if read == '':
      Trace.error('EOF reached')
      return 0
    tuple = struct.unpack(format, read)
    return tuple[0]

  def seek(self, file, bytes):
    "Seek forward, just by reading the given number of bytes"
    file.read(bytes)

class ImageOutput(object):
  "Returns an image in the output"

  def gethtml(self, container):
    "Get the HTML output of the image as a list"
    html = ['<img class="' + container.type + '"']
    if container.origin.exists():
      html += self.getimagehtml(container)
    else:
      html.append(' src="' + container.origin.url + '"')
    html.append('/>\n')
    return html

  def getimagehtml(self, container):
    "Get the HTML corresponding to the image."
    if container.width and not container.height:
      container.height = 'auto'
    if container.height and not container.width:
      container.width = 'auto'
    html = []
    figure = Translator.translate('figure')
    html.append(' src="' + container.destination.url +
        '" alt="' + figure + ' ' + container.destination.url + '"')
    html.append(' style="')
    if container.width:
      html.append('width: ' + container.width + '; ')
    if container.maxwidth:
      html.append('max-width: ' + container.maxwidth + '; ')
    if container.height:
      html.append('height: ' + container.height + '; ')
    if container.maxheight:
      html.append('max-height: ' + container.maxheight + '; ')
    html.append('"')
    return html






class ListItem(Container):
  "An element in a list"

  def __init__(self):
    "Output should be empty until the postprocessor can group items"
    self.contents = list()
    self.parser = BoundedParser()
    self.output = EmptyOutput()

  def process(self):
    "Set the correct type and contents."
    self.type = self.header[1]
    tag = TaggedText().complete(self.contents, 'li', True)
    self.contents = [tag]

  def __unicode__(self):
    return self.type + ' item @ ' + unicode(self.begin)

class DeeperList(Container):
  "A nested list"

  def __init__(self):
    "Output should be empty until the postprocessor can group items"
    self.parser = BoundedParser()
    self.output = EmptyOutput()

  def process(self):
    "Create the deeper list"
    if len(self.contents) == 0:
      Trace.error('Empty deeper list')
      return

  def __unicode__(self):
    result = 'deeper list @ ' + unicode(self.begin) + ': ['
    for element in self.contents:
      result += unicode(element) + ', '
    return result[:-2] + ']'

class PendingList(object):
  "A pending list"

  def __init__(self):
    self.contents = []
    self.type = None

  def additem(self, item):
    "Add a list item"
    self.contents += item.contents
    if not self.type:
      self.type = item.type

  def adddeeper(self, deeper):
    "Add a deeper list item"
    if self.empty():
      self.insertfake()
    item = self.contents[-1]
    self.contents[-1].contents += deeper.contents

  def generate(self):
    "Get the resulting list"
    if not self.type:
      tag = 'ul'
    else:
      tag = TagConfig.listitems[self.type]
    text = TaggedText().complete(self.contents, tag, True)
    self.__init__()
    return text

  def isduewithitem(self, item):
    "Decide whether the pending list must be generated before the given item"
    if not self.type:
      return False
    if self.type != item.type:
      return True
    return False

  def isduewithnext(self, next):
    "Applies only if the list is finished with next item."
    if not next:
      return True
    if not isinstance(next, ListItem) and not isinstance(next, DeeperList):
      return True
    return False

  def empty(self):
    return len(self.contents) == 0

  def insertfake(self):
    "Insert a fake item"
    item = TaggedText().constant('', 'li class="nested"', True)
    self.contents = [item]
    self.type = 'Itemize'

  def __unicode__(self):
    result = 'pending ' + unicode(self.type) + ': ['
    for element in self.contents:
      result += unicode(element) + ', '
    if len(self.contents) > 0:
      result = result[:-2]
    return result + ']'

class PostListItem(object):
  "Postprocess a list item"

  processedclass = ListItem

  def postprocess(self, last, item, next):
    "Add the item to pending and return an empty item"
    if not hasattr(self.postprocessor, 'list'):
      self.postprocessor.list = PendingList()
    self.postprocessor.list.additem(item)
    if self.postprocessor.list.isduewithnext(next):
      return self.postprocessor.list.generate()
    if isinstance(next, ListItem) and self.postprocessor.list.isduewithitem(next):
      return self.postprocessor.list.generate()
    return BlackBox()

class PostDeeperList(object):
  "Postprocess a deeper list"

  processedclass = DeeperList

  def postprocess(self, last, deeper, next):
    "Append to the list in the postprocessor"
    if not hasattr(self.postprocessor, 'list'):
      self.postprocessor.list = PendingList()
    self.postprocessor.list.adddeeper(deeper)
    if self.postprocessor.list.isduewithnext(next):
      return self.postprocessor.list.generate()
    return BlackBox()

Postprocessor.stages += [PostListItem, PostDeeperList]







import os
import sys
import codecs


class BulkFile(object):
  "A file to treat in bulk"

  def __init__(self, filename):
    self.filename = filename
    self.temp = self.filename + '.temp'

  def readall(self):
    "Read the whole file"
    for encoding in FileConfig.parsing['encodings']:
      try:
        return self.readcodec(encoding)
      except UnicodeDecodeError:
        pass
    Trace.error('No suitable encoding for ' + self.filename)
    return []

  def readcodec(self, encoding):
    "Read the whole file with the given encoding"
    filein = codecs.open(self.filename, 'rU', encoding)
    lines = filein.readlines()
    filein.close()
    return lines

  def getfiles(self):
    "Get reader and writer for a file name"
    reader = LineReader(self.filename)
    writer = LineWriter(self.temp)
    return reader, writer

  def swaptemp(self):
    "Swap the temp file for the original"
    os.chmod(self.temp, os.stat(self.filename).st_mode)
    os.rename(self.temp, self.filename)

  def __unicode__(self):
    "Get the unicode representation"
    return 'file ' + self.filename



class InsetText(Container):
  "An inset of text in a lyx file"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = ContentsOutput()

class Inset(Container):
  "A generic inset in a LyX document"

  def __init__(self):
    self.contents = list()
    self.parser = InsetParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.type = self.header[1]
    self.output.tag = 'span class="' + self.type + '"'

  def __unicode__(self):
    return 'Inset of type ' + self.type

class NewlineInset(Newline):
  "A newline or line break in an inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class NewPageInset(NewPage):
  "A new page command."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class Branch(Container):
  "A branch within a LyX document"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="branch"', True)

  def process(self):
    "Disable inactive branches"
    self.branch = self.header[2]
    if not self.isactive():
      Trace.debug('Branch ' + self.branch + ' not active')
      self.output = EmptyOutput()

  def isactive(self):
    "Check if the branch is active"
    if not self.branch in Options.branches:
      Trace.error('Invalid branch ' + self.branch)
      return True
    branch = Options.branches[self.branch]
    return branch.isselected()

class ShortTitle(Container):
  "A short title to display (always hidden)"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

class SideNote(Container):
  "A side note that appears at the right."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput()

  def process(self):
    "Enclose everything in a marginal span."
    self.output.settag('span class="Marginal"', True)

class Footnote(Container):
  "A footnote to the main text"

  order = 0

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Add a letter for the order, rotating"
    if Options.numberfoot:
      letter = NumberGenerator.instance.generateunique('Footnote')
    else:
      letter = NumberGenerator.instance.letter(Footnote.order)
    span = 'span class="FootMarker"'
    pre = FootnoteConfig.constants['prefrom']
    post = FootnoteConfig.constants['postfrom']
    fromfoot = TaggedText().constant(pre + letter + post, span)
    self.contents.insert(0, fromfoot)
    tag = TaggedText().complete(self.contents, 'span class="Foot"', True)
    pre = FootnoteConfig.constants['preto']
    post = FootnoteConfig.constants['postto']
    tofoot = TaggedText().constant(pre + letter + post, span)
    self.contents = [tofoot, tag]
    Footnote.order += 1

class Note(Container):
  "A LyX note of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

  def process(self):
    "Hide note and comment, dim greyed out"
    self.type = self.header[2]
    if TagConfig.notes[self.type] == '':
      return
    self.output = TaggedOutput().settag(TagConfig.notes[self.type], True)

class FlexInset(Container):
  "A flexible inset, generic version."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span', False)

  def process(self):
    "Set the correct flex tag."
    self.type = self.header[2]
    if not self.type in TagConfig.flex:
      Trace.error('Unknown Flex inset ' + self.type)
      return
    self.output.settag(TagConfig.flex[self.type], False)

class InfoInset(Container):
  "A LyX Info inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="Info"', False)

  def process(self):
    "Set the shortcut as text"
    self.type = self.parameters['type']
    self.contents = [Constant(self.parameters['arg'])]

class BoxInset(Container):
  "A box inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div', True)

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    self.output.settag('div class="' + self.type + '"', True)

class VerticalSpace(Container):
  "An inset that contains a vertical space."

  def __init__(self):
    self.parser = InsetParser()

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    self.output = TaggedOutput().settag('div class="' + self.type + '"', True)

class IncludeInset(Container):
  "A child document included within another."

  # the converter factory will be set in converter.py
  converterfactory = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()
    self.postprocess = False

  def process(self):
    "Include the provided child document"
    self.filename = os.path.join(Options.directory, self.parameters['filename'])
    Trace.debug('Child document: ' + self.filename)
    LstParser().parsecontainer(self)
    if 'LatexCommand' in self.parameters:
      if self.parameters['LatexCommand'] == 'verbatiminput':
        self.readverbatim()
        return
      if self.parameters['LatexCommand'] == 'lstinputlisting':
        self.readlisting()
        return

    olddir = Options.directory
    newdir = os.path.dirname(self.parameters['filename'])
    if newdir != '':
      Trace.debug('Child dir: ' + newdir)
      Options.directory = os.path.join(Options.directory, newdir)
    try:
      converter = IncludeInset.converterfactory.create(self)
      converter.convert()
      self.contents = converter.getcontents()
    except:
      Trace.error('Could not read ' + self.filename + ', please check that the file exists and has read permissions.')
      self.contents = []
    finally:
      Options.directory = olddir

  def readverbatim(self):
    "Read a verbatim document."
    verbatim = list()
    lines = BulkFile(self.filename).readall()
    for line in lines:
      verbatim.append(Constant(line))
    self.contents = [TaggedText().complete(verbatim, 'pre', True)]

  def readlisting(self):
    "Read a document and create a program listing"
    lines = BulkFile(self.filename).readall()
    newcontents = []
    for line in lines:
      newcontents.append(Constant(self.escape(line)))
      
    self.output = TaggedOutput().settag('div class="listing"', True)

    lang = 'scala'
    if 'language' in self.lstparams:
      lang = self.lstparams['language']

    tagged = TaggedText().complete(newcontents, 
             'pre class="listing brush: '+lang+'"', False)
    self.contents = [tagged]



class Float(Container):
  "A floating inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="float"', True)
    self.parentfloat = None
    self.children = []
    self.number = None

  def process(self):
    "Get the float type."
    self.type = self.header[2]
    self.processfloats()
    self.processtags()
    self.chapter = NumberGenerator.instance.getchapter()

  def processtags(self):
    "Process the HTML tags."
    embeddedtag = self.getembeddedtag()
    wideningtag = self.getwideningtag()
    self.embed(embeddedtag + wideningtag)

  def processfloats(self):
    "Process all floats contained inside."
    floats = self.searchall(Float)
    for float in floats:
      float.output.tag = float.output.tag.replace('div', 'span')
      float.parentfloat = self
      self.children.append(float)

  def getembeddedtag(self):
    "Get the tag for the embedded object."
    floats = self.searchall(Float)
    if len(floats) > 0:
      return 'div class="multi' + self.type + '"'
    return 'div class="' + self.type + '"'

  def getwideningtag(self):
    "Get the tag to set float width, if present."
    images = self.searchall(Image)
    if len(images) != 1:
      return ''
    image = images[0]
    if not image.width:
      return ''
    if not '%' in image.width:
      return ''
    image.type = 'figure'
    width = image.width
    image.width = None
    return ' style="max-width: ' + width + ';"'

  def embed(self, tag):
    "Embed the whole contents in a div"
    tagged = TaggedText().complete(self.contents, tag, True)
    self.contents = [tagged]

  def searchinside(self, type):
    "Search for a given type in the contents"
    return self.searchincontents(self.contents, type)

  def searchincontents(self, contents, type):
    "Search in the given contents for the required type."
    list = []
    for element in contents:
      list += self.searchinelement(element, type)
    return list

  def searchinelement(self, element, type):
    "Search for a given type outside floats"
    if isinstance(element, Float):
      return []
    if isinstance(element, type):
      return [element]
    return self.searchincontents(element.contents, type)

  def __unicode__(self):
    "Return a printable representation"
    return 'Floating inset of type ' + self.type

class Wrap(Float):
  "A wrapped (floating) float"

  def processtags(self):
    "Add the widening tag to the parent tag."
    embeddedtag = self.getembeddedtag()
    self.embed(embeddedtag)
    placement = self.parameters['placement']
    wideningtag = self.getwideningtag()
    self.output.tag = 'div class="wrap-' + placement + '"' + wideningtag

class Caption(Container):
  "A caption for a figure or a table"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="caption"', True)

class Listing(Container):
  "A code listing"

  processor = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="listing"', True)
    self.numbered = None

  def process(self):
    "Remove all layouts"
    self.counter = 0
    self.type = 'listing'
    self.processparams()
    if Listing.processor:
      Listing.processor.preprocess(self)
    newcontents = []
    for container in self.contents:
      newcontents += self.extract(container)
    lang = 'scala'
    if 'language' in self.lstparams:
      lang = self.lstparams['language']

    tagged = TaggedText().complete(newcontents, 'pre class="listing brush: '+lang+'"', False)
    self.contents = [tagged]
    if Listing.processor:
      Listing.processor.postprocess(self)

  def processparams(self):
    "Process listing parameteres."
    LstParser().parsecontainer(self)
    if not 'numbers' in self.lstparams:
      return
    self.numbered = self.lstparams['numbers']

  def extract(self, container):
    "Extract the container's contents and return them"
    if isinstance(container, StringContainer):
      return self.modifystring(container)
    if isinstance(container, StandardLayout):
      return self.modifylayout(container)
    if isinstance(container, PlainLayout):
      return self.modifylayout(container)
    Trace.error('Unexpected container ' + container.__class__.__name__ +
        ' in listing')
    container.tree()
    return []

  def modifystring(self, string):
    "Modify a listing string"
    if string.string == '':
      string.string = u'​'
    return self.modifycontainer(string)

  def modifylayout(self, layout):
    "Modify a standard layout"
    if len(layout.contents) == 0:
      layout.contents = [Constant(u'​')]
    return self.modifycontainer(layout)

  def modifycontainer(self, container):
    "Modify a listing container"
    contents = [container, Constant('\n')]
    if self.numbered:
      self.counter += 1
      tag = 'span class="number-' + self.numbered + '"'
      contents.insert(0, TaggedText().constant(unicode(self.counter), tag))
    return contents

class FloatNumber(Container):
  "Holds the number for a float in the caption."

  def __init__(self):
    self.output = ContentsOutput()

  def create(self, float):
    "Create the float number."
    self.contents = [Constant(float.entry)]
    return self

class PostFloat(object):
  "Postprocess a float: number it and move the label"

  processedclass = Float

  def postprocess(self, last, float, next):
    "Move the label to the top and number the caption"
    self.postnumber(float)
    number = FloatNumber().create(float)
    for caption in float.searchinside(Caption):
      self.postlabels(float, caption)
      caption.contents.insert(0, Constant(u' '))
      caption.contents.insert(0, number)
    return float

  def postlabels(self, float, caption):
    "Search for labels and move them to the top"
    labels = caption.searchremove(Label)
    if len(labels) == 0:
      labels = [Label().create(' ', float.entry.replace(' ', '-'))]
    float.contents = labels + float.contents

  def postnumber(self, float):
    "Number a float if it isn't numbered."
    if float.number:
      return
    if float.parentfloat:
      self.postnumber(float.parentfloat)
      index = float.parentfloat.children.index(float)
      float.number = NumberGenerator.instance.letter(index).lower()
      float.entry = '(' + float.number + ')'
    else:
      float.number = NumberGenerator.instance.generatechaptered(float.type, float.chapter)
      float.entry = Translator.translate('float-' + float.type) + float.number

class PostWrap(PostFloat):
  "For a wrap: exactly like a float"

  processedclass = Wrap

Postprocessor.stages += [PostFloat, PostWrap]




import sys


class FormulaEquation(CommandBit):
  "A simple numbered equation."

  piece = 'equation'

  def parsebit(self, pos):
    "Parse the array"
    self.output = ContentsOutput()
    inner = WholeFormula()
    inner.parsebit(pos)
    self.add(inner)

class FormulaCell(FormulaCommand):
  "An array cell inside a row"

  def __init__(self, alignment):
    FormulaCommand.__init__(self)
    self.alignment = alignment
    self.output = TaggedOutput().settag('td class="formula-' + alignment +'"', True)

  def parsebit(self, pos):
    formula = WholeFormula()
    if not formula.detect(pos):
      Trace.error('Unexpected end of array cell at ' + pos.identifier())
      pos.skip(pos.current())
      return
    formula.parsebit(pos)
    self.add(formula)

class FormulaRow(FormulaCommand):
  "An array row inside an array"

  cellseparator = FormulaConfig.array['cellseparator']

  def __init__(self, alignments):
    FormulaCommand.__init__(self)
    self.alignments = alignments
    self.output = TaggedOutput().settag('tr', True)

  def parsebit(self, pos):
    "Parse a whole row"
    index = 0
    pos.pushending(FormulaRow.cellseparator, optional=True)
    while not pos.finished():
      alignment = self.alignments[index % len(self.alignments)]
      cell = FormulaCell(alignment)
      cell.parsebit(pos)
      self.add(cell)
      index += 1
      pos.checkskip(FormulaRow.cellseparator)
    return
    for cell in self.iteratecells(pos):
      cell.parsebit(pos)
      self.add(cell)

  def iteratecells(self, pos):
    "Iterate over all cells, finish when count ends"
    for index, alignment in enumerate(self.alignments):
      if self.anybutlast(index):
        pos.pushending(cellseparator)
      yield FormulaCell(alignment)
      if self.anybutlast(index):
        if not pos.checkfor(cellseparator):
          Trace.error('No cell separator ' + cellseparator)
        else:
          self.original += pos.popending(cellseparator)

  def anybutlast(self, index):
    "Return true for all cells but the last"
    return index < len(self.alignments) - 1

class MultiRowFormula(CommandBit):
  "A formula with multiple rows."

  def parserows(self, pos):
    "Parse all rows, finish when no more row ends"
    for row in self.iteraterows(pos):
      row.parsebit(pos)
      self.add(row)

  def iteraterows(self, pos):
    "Iterate over all rows, end when no more row ends"
    rowseparator = FormulaConfig.array['rowseparator']
    while True:
      pos.pushending(rowseparator, True)
      yield FormulaRow(self.alignments)
      if pos.checkfor(rowseparator):
        self.original += pos.popending(rowseparator)
      else:
        return

class FormulaArray(MultiRowFormula):
  "An array within a formula"

  piece = 'array'

  def parsebit(self, pos):
    "Parse the array"
    self.output = TaggedOutput().settag('table class="formula"', True)
    self.parsealignments(pos)
    self.parserows(pos)

  def parsealignments(self, pos):
    "Parse the different alignments"
    # vertical
    self.valign = 'c'
    literal = self.parsesquareliteral(pos)
    if literal:
      self.valign = literal
    # horizontal
    literal = self.parseliteral(pos)
    self.alignments = []
    for l in literal:
      self.alignments.append(l)

class FormulaCases(MultiRowFormula):
  "A cases statement"

  piece = 'cases'

  def parsebit(self, pos):
    "Parse the cases"
    self.output = TaggedOutput().settag('table class="cases"', True)
    self.alignments = ['l', 'l']
    self.parserows(pos)

class EquationEnvironment(MultiRowFormula):
  "A \\begin{}...\\end equation environment with rows and cells."

  def parsebit(self, pos):
    "Parse the whole environment."
    self.output = TaggedOutput().settag('table class="environment"', True)
    environment = self.piece.replace('*', '')
    if environment in FormulaConfig.environments:
      self.alignments = FormulaConfig.environments[environment]
    else:
      Trace.error('Unknown equation environment ' + self.piece)
      self.alignments = ['l']
    self.parserows(pos)

class BeginCommand(CommandBit):
  "A \\begin{}...\end command and what it entails (array, cases, aligned)"

  commandmap = {FormulaConfig.array['begin']:''}

  innerbits = [FormulaEquation(), FormulaArray(), FormulaCases()]

  def parsebit(self, pos):
    "Parse the begin command"
    literal = self.parseliteral(pos)
    bit = self.findbit(literal)
    ending = FormulaConfig.array['end'] + '{' + literal + '}'
    pos.pushending(ending)
    bit.parsebit(pos)
    self.add(bit)
    self.original += pos.popending(ending)

  def findbit(self, piece):
    "Find the command bit corresponding to the \\begin{piece}"
    for bit in BeginCommand.innerbits:
      if bit.piece == piece:
        newbit = Cloner.clone(bit)
        return newbit
    bit = EquationEnvironment()
    bit.piece = piece
    return bit

FormulaCommand.commandbits += [BeginCommand()]






class BibTeX(Container):
  "Show a BibTeX bibliography and all referenced entries"

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Read all bibtex files and process them"
    self.entries = []
    bibliography = Translator.translate('bibliography')
    tag = TaggedText().constant(bibliography, 'h1 class="biblio"', True)
    self.contents.append(tag)
    files = self.parameters['bibfiles'].split(',')
    for file in files:
      bibfile = BibFile(file)
      bibfile.parse()
      self.entries += bibfile.entries
      Trace.message('Parsed ' + unicode(bibfile))
    self.entries.sort(key = unicode)
    self.applystyle()

  def applystyle(self):
    "Read the style and apply it to all entries"
    style = self.readstyle()
    for entry in self.entries:
      entry.template = style['default']
      type = entry.type.lower()
      if type in style:
        entry.template = style[type]
      entry.process()
      self.contents.append(entry)

  def readstyle(self):
    "Read the style from the bibliography options"
    options = self.parameters['options'].split(',')
    for option in options:
      if hasattr(BibStylesConfig, option):
        return getattr(BibStylesConfig, option)
    return BibStylesConfig.default

class BibFile(object):
  "A BibTeX file"

  def __init__(self, filename):
    "Create the BibTeX file"
    self.filename = filename + '.bib'
    self.added = 0
    self.ignored = 0
    self.entries = []

  def parse(self):
    "Parse the BibTeX file and extract all entries."
    try:
      self.parsefile()
    except IOError:
      Trace.error('Error reading ' + self.filename + '; make sure the file exists and can be read.')

  def parsefile(self):
    "Parse the whole file."
    bibpath = InputPath(self.filename)
    if Options.lowmem:
      pos = FilePosition(bibpath.path)
    else:
      bulkfile = BulkFile(bibpath.path)
      text = ''.join(bulkfile.readall())
      pos = TextPosition(text)
    while not pos.finished():
      pos.skipspace()
      self.parseentry(pos)

  def parseentry(self, pos):
    "Parse a single entry"
    for entry in Entry.entries:
      if entry.detect(pos):
        newentry = Cloner.clone(entry)
        newentry.parse(pos)
        if newentry.isreferenced():
          self.entries.append(newentry)
          self.added += 1
        else:
          self.ignored += 1
        return
    # Skip the whole line, and show it as an error
    pos.checkskip('\n')
    Entry.entries[0].lineerror('Unidentified entry', pos)

  def __unicode__(self):
    "String representation"
    string = self.filename + ': ' + unicode(self.added) + ' entries added, '
    string += unicode(self.ignored) + ' entries ignored'
    return string

class Entry(Container):
  "An entry in a BibTeX file"

  entries = []

  def lineerror(self, message, pos):
    "Show an error message for a line."
    Trace.error(message + ': ' + pos.identifier())
    pos.globincluding('\n')

class CommentEntry(Entry):
  "A simple comment."

  def detect(self, pos):
    "Detect the special entry"
    return pos.checkfor('%')

  def parse(self, pos):
    "Parse all consecutive comment lines."
    while pos.checkfor('%'):
      pos.globincluding('\n')

  def isreferenced(self):
    "A comment entry is never referenced"
    return False

  def __unicode__(self):
    "Return a string representation"
    return 'Comment'

class ContentEntry(Entry):
  "An entry holding some content."

  nameseparators = ['{', '=', '"', '#']
  valueseparators = ['{', '"', '#', '\\', '}']

  def __init__(self):
    self.key = None
    self.tags = dict()
    self.output = TaggedOutput().settag('p class="biblio"', True)

  def parse(self, pos):
    "Parse the entry between {}"
    self.type = self.parsepiece(pos, self.nameseparators)
    pos.skipspace()
    if not pos.checkskip('{'):
      self.lineerror('Entry should start with {', pos)
      return
    pos.pushending('}')
    self.parsetags(pos)
    pos.popending('}')
    pos.skipspace()

  def parsetags(self, pos):
    "Parse all tags in the entry"
    pos.skipspace()
    while not pos.finished():
      if pos.checkskip('{'):
        self.lineerror('Unmatched {', pos)
        return
      pos.pushending(',', True)
      self.parsetag(pos)
      if pos.checkfor(','):
        pos.popending(',')
  
  def parsetag(self, pos):
    piece = self.parsepiece(pos, self.nameseparators)
    if pos.finished():
      self.key = piece
      return
    if not pos.checkskip('='):
      self.lineerror('Undesired character in tag name ' + piece, pos)
      return
    name = piece.lower().strip()
    pos.skipspace()
    value = self.parsevalue(pos)
    self.tags[name] = value
    if not pos.finished():
      remainder = pos.globexcluding(',')
      self.lineerror('Ignored ' + remainder + ' before comma', pos)

  def parsevalue(self, pos):
    "Parse the value for a tag"
    pos.skipspace()
    if pos.checkfor(','):
      self.lineerror('Unexpected ,', pos)
      return ''
    return self.parserecursive(pos)

  def parserecursive(self, pos):
    "Parse brackets or quotes recursively."
    contents = ''
    while not pos.finished():
      contents += self.parsepiece(pos, self.valueseparators)
      if pos.finished():
        return contents
      if pos.checkfor('{'):
        contents += self.parsebracket(pos)
      elif pos.checkfor('"'):
        contents += self.parsequoted(pos)
      elif pos.checkfor('\\'):
        contents += self.parseescaped(pos)
      elif pos.checkskip('#'):
        pos.skipspace()
      else:
        self.lineerror('Unexpected character ' + pos.current(), pos)
        pos.currentskip()
    return contents

  def parseescaped(self, pos):
    "Parse an escaped character \\*."
    if not pos.checkskip('\\'):
      self.lineerror('Not an escaped character', pos)
      return ''
    if not pos.checkskip('{'):
      return '\\' + pos.currentskip()
    current = pos.currentskip()
    if not pos.checkskip('}'):
      self.lineerror('Weird escaped but unclosed brackets \\{*', pos)
    return '\\' + current

  def parsebracket(self, pos):
    "Parse a {} bracket"
    if not pos.checkskip('{'):
      self.lineerror('Missing opening { in bracket', pos)
      return ''
    pos.pushending('}')
    bracket = self.parserecursive(pos)
    pos.popending('}')
    return bracket

  def parsequoted(self, pos):
    "Parse a piece of quoted text"
    if not pos.checkskip('"'):
      self.lineerror('Missing opening " in quote', pos)
      return ''
    pos.pushending('"', True)
    quoted = self.parserecursive(pos)
    pos.popending('"')
    pos.skipspace()
    return quoted

  def parsepiece(self, pos, undesired):
    "Parse a piece not structure."
    return pos.glob(lambda current: not current in undesired)

class SpecialEntry(ContentEntry):
  "A special entry"

  types = ['@STRING', '@PREAMBLE', '@COMMENT']

  def detect(self, pos):
    "Detect the special entry"
    for type in SpecialEntry.types:
      if pos.checkfor(type):
        return True
    return False

  def isreferenced(self):
    "A special entry is never referenced"
    return False

  def __unicode__(self):
    "Return a string representation"
    return self.type

class PubEntry(ContentEntry):
  "A publication entry"

  escaped = BibTeXConfig.escaped

  def detect(self, pos):
    "Detect a publication entry"
    return pos.checkfor('@')

  def isreferenced(self):
    "Check if the entry is referenced"
    if not self.key:
      return False
    return self.key in BiblioReference.references

  def process(self):
    "Process the entry"
    self.index = NumberGenerator.instance.generateunique('pubentry')
    biblio = BiblioEntry()
    biblio.processcites(self.key)
    self.contents = [biblio, Constant(' ')]
    self.contents.append(self.getcontents())

  def getcontents(self):
    "Get the contents as a constant"
    contents = self.template
    while contents.find('$') >= 0:
      contents = self.replacetag(contents)
    return Constant(self.escapeentry(contents))

  def replacetag(self, string):
    "Replace a tag with its value."
    tag = self.extracttag(string)
    value = self.gettag(tag)
    dollar = string.find('$' + tag)
    begin = string.rfind('{', 0, dollar)
    end = string.find('}', dollar)
    if begin != -1 and end != -1 and begin < end:
      bracket = string[begin + 1:end]
      if not value:
        result = ''
      else:
        result = bracket.replace('$' + tag, value)
      return string[0:begin] + result + string[end + 1:]
    if not value:
      value = ''
    return string.replace('$' + tag, value)

  def extracttag(self, string):
    "Extract the first tag in the form $tag"
    result = ''
    index = string.index('$') + 1
    while string[index].isalpha():
      result += string[index]
      index += 1
    return result

  def gettag(self, key):
    "Get a tag with the given key"
    if not key in self.tags:
      return None
    return self.tags[key]

  def escapeentry(self, string):
    "Escape a string."
    for escape in self.escaped:
      if escape in string:
        string = string.replace(escape, self.escaped[escape])
    return string

  def __unicode__(self):
    "Return a string representation"
    string = ''
    author = self.gettag('author')
    if author:
      string += author + ': '
    title = self.gettag('title')
    if title:
      string += '"' + title + '"'
    return string

Entry.entries += [CommentEntry(), SpecialEntry(), PubEntry()]






class NewfangledChunk(Layout):
  "A chunk of literate programming."

  names = dict()
  firsttime = True

  def process(self):
    "Process the literate chunk."
    self.output.tag = 'div class="chunk"'
    self.type = 'chunk'
    text = self.extracttext()
    parts = text.split(',')
    if len(parts) < 1:
      Trace.error('Not enough parameters in ' + text)
      return
    self.name = parts[0]
    self.number = self.order()
    self.createlinks()
    self.contents = [self.left, self.declaration(), self.right]
    ChunkProcessor.lastchunk = self

  def order(self):
    "Create the order number for the chunk."
    return NumberGenerator.instance.generateunique('chunk')

  def createlinks(self):
    "Create back and forward links."
    self.leftlink = Link().complete(self.number, 'chunk:' + self.number, type='chunk')
    self.left = TaggedText().complete([self.leftlink], 'span class="chunkleft"', False)
    self.right = TaggedText().constant('', 'span class="chunkright"', False)
    if not self.name in NewfangledChunk.names:
      NewfangledChunk.names[self.name] = []
    else:
      last = NewfangledChunk.names[self.name][-1]
      forwardlink = Link().complete(self.number + u'→', 'chunkback:' + last.number, type='chunk')
      backlink = Link().complete(u'←' + last.number + u' ', 'chunkforward:' + self.number, type='chunk')
      forwardlink.setmutualdestination(backlink)
      last.right.contents.append(forwardlink)
      self.right.contents.append(backlink)
    NewfangledChunk.names[self.name].append(self)
    self.origin = self.createorigin()
    if self.name in NewfangledChunkRef.references:
      for ref in NewfangledChunkRef.references[self.name]:
        self.linkorigin(ref.origin)

  def createorigin(self):
    "Create a link that points to the chunks' origin."
    link = Link()
    self.linkorigin(link)
    return link

  def linkorigin(self, link):
    "Create a link to the origin."
    start = NewfangledChunk.names[self.name][0]
    link.complete(start.number, type='chunk')
    link.destination = start.leftlink
    link.computedestination()

  def declaration(self):
    "Get the chunk declaration."
    contents = []
    text = u'⟨' + self.name + '[' + unicode(len(NewfangledChunk.names[self.name])) + '] '
    contents.append(Constant(text))
    contents.append(self.origin)
    text = ''
    if NewfangledChunk.firsttime:
      Listing.processor = ChunkProcessor()
      NewfangledChunk.firsttime = False
    text += u'⟩'
    if len(NewfangledChunk.names[self.name]) > 1:
      text += '+'
    text += u'≡'
    contents.append(Constant(text))
    return TaggedText().complete(contents, 'span class="chunkdecl"', True)

class ChunkProcessor(object):
  "A processor for listings that belong to chunks."

  lastchunk = None
  counters = dict()
  endcommand = '}'
  chunkref = 'chunkref'

  def preprocess(self, listing):
    "Preprocess a listing: set the starting counter."
    if not ChunkProcessor.lastchunk:
      return
    name = ChunkProcessor.lastchunk.name
    if not name in ChunkProcessor.counters:
      ChunkProcessor.counters[name] = 0
    listing.counter = ChunkProcessor.counters[name]
    for command, container, index in self.commandsinlisting(listing):
      chunkref = self.getchunkref(command)
      if chunkref:
        self.insertchunkref(chunkref, container, index)

  def commandsinlisting(self, listing):
    "Find all newfangle commands in a listing."
    for container in listing.contents:
      for index in range(len(container.contents) - 2):
        if self.findinelement(container, index):
          third = container.contents[index + 2].string
          end = third.index(NewfangleConfig.constants['endmark'])
          command = third[:end]
          lenstart = len(NewfangleConfig.constants['startmark'])
          container.contents[index].string = container.contents[index].string[:-lenstart]
          del container.contents[index + 1]
          container.contents[index + 1].string = third[end + len(NewfangleConfig.constants['endmark']):]
          yield command, container, index

  def findinelement(self, container, index):
    "Find a newfangle command in an element."
    for i in range(2):
      if not isinstance(container.contents[index + i], StringContainer):
        return False
    first = container.contents[index].string
    second = container.contents[index + 1].string
    third = container.contents[index + 2].string
    if not first.endswith(NewfangleConfig.constants['startmark']):
      return False
    if second != NewfangleConfig.constants['startcommand']:
      return False
    if not NewfangleConfig.constants['endmark'] in third:
      return False
    return True

  def getchunkref(self, command):
    "Get the contents of a chunkref command, if present."
    if not command.startswith(NewfangleConfig.constants['chunkref']):
      return None
    if not NewfangleConfig.constants['endcommand'] in command:
      return None
    start = len(NewfangleConfig.constants['chunkref'])
    end = command.index(NewfangleConfig.constants['endcommand'])
    return command[start:end]

  def insertchunkref(self, ref, container, index):
    "Insert a chunkref after the given index at the given container."
    chunkref = NewfangledChunkRef().complete(ref)
    container.contents.insert(index + 1, chunkref)

  def postprocess(self, listing):
    "Postprocess a listing: store the ending counter for next chunk."
    if not ChunkProcessor.lastchunk:
      return
    ChunkProcessor.counters[ChunkProcessor.lastchunk.name] = listing.counter

class NewfangledChunkRef(Inset):
  "A reference to a chunk."

  references = dict()

  def process(self):
    "Show the reference."
    self.output.tag = 'span class="chunkref"'
    self.ref = self.extracttext()
    self.addbits()

  def complete(self, ref):
    "Complete the reference to the given string."
    self.output = ContentsOutput()
    self.ref = ref
    self.contents = [Constant(self.ref)]
    self.addbits()
    return self

  def addbits(self):
    "Add the bits to the reference."
    if not self.ref in NewfangledChunkRef.references:
      NewfangledChunkRef.references[self.ref] = []
    NewfangledChunkRef.references[self.ref].append(self)
    if self.ref in NewfangledChunk.names:
      start = NewfangledChunk.names[self.ref][0]
      self.origin = start.createorigin()
    else:
      self.origin = Link()
    self.contents.insert(0, Constant(u'⟨'))
    self.contents.append(Constant(' '))
    self.contents.append(self.origin)
    self.contents.append(Constant(u'⟩'))

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference to chunk ' + self.ref






class MathMacro(object):
  "A math macro: command, parameters, default values, definition."

  macros = dict()

  def __init__(self):
    self.newcommand = None
    self.parameters = 0
    self.defaults = []
    self.definition = None

  def instantiate(self):
    "Return an instance of the macro."
    return self.definition.clone()

  def parsepreamble(self):
    "Parse the LyX preamble, if needed."
    if len(PreambleParser.preamble) == 0:
      return
    FormulaCommand.preambling = True
    pos = TextPosition('\n'.join(PreambleParser.preamble))
    while not pos.finished():
      if self.detectdefinition(pos):
        self.parsedefinition(pos)
      else:
        pos.globincluding('\n')
    PreambleParser.preamble = []
    FormulaCommand.preambling = False

  def detectdefinition(self, pos):
    "Detect a macro definition."
    for function in FormulaConfig.definingfunctions:
      if pos.checkfor(function):
        return True
    return False

  def parsedefinition(self, pos):
    "Parse a macro definition."
    command = FormulaCommand()
    command.factory = FormulaFactory()
    bit = command.parsebit(pos)
    if not isinstance(bit, DefiningFunction):
      Trace.error('Did not define a macro with ' + unicode(bit))

Formula.initializations.append(MathMacro().parsepreamble)

class MacroParameter(FormulaBit):
  "A parameter from a macro."

  def detect(self, pos):
    "Find a macro parameter: #n."
    return pos.checkfor('#')

  def parsebit(self, pos):
    "Parse the parameter: #n."
    if not pos.checkskip('#'):
      Trace.error('Missing parameter start #.')
      return
    self.number = int(pos.currentskip())
    self.original = '#' + unicode(self.number)
    self.contents = [TaggedBit().constant('#' + unicode(self.number), 'span class="unknown"')]

class DefiningFunction(HybridFunction):
  "Read a function that defines a new command (a macro)."

  commandmap = FormulaConfig.definingfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters."
    if Bracket().detect(pos):
      newcommand = self.parseliteral(pos)
    elif FormulaCommand().detect(pos):
      newcommand = FormulaCommand().extractcommand(pos)
    else:
      Trace.error('Unknown formula bit in defining function at ' + pos.identifier())
    Trace.debug('New command: ' + newcommand)
    HybridFunction.parsebit(self, pos)
    macro = MathMacro()
    macro.newcommand = newcommand
    macro.parameters = self.readparameters()
    macro.definition = self.params['$d'].value
    for index in range(9):
      value = self.extractdefault(index + 1)
      if value:
        macro.defaults.append(value)
      else:
        break
    MathMacro.macros[newcommand] = macro

  def readparameters(self):
    "Read the number of parameters in the macro."
    if not self.params['$n'].literalvalue:
      return 0
    return int(self.params['$n'].literalvalue)

  def extractdefault(self, index):
    "Extract the default value for parameter index."
    value = self.params['$' + unicode(index)].value
    if not value:
      return None
    if len(value.contents) == 0:
      return FormulaConstant('')
    return value.contents[0]

class MacroFunction(CommandBit):
  "A function that was defined using a macro."

  commandmap = MathMacro.macros

  def parsebit(self, pos):
    "Parse a number of input parameters."
    self.values = []
    macro = self.translated
    while self.factory.detectbit(pos):
      self.values.append(self.parseparameter(pos))
    defaults = list(macro.defaults)
    while len(self.values) < macro.parameters and len(defaults) > 0:
      self.values.insert(0, defaults.pop())
    if len(self.values) < macro.parameters:
      Trace.error('Missing parameters in macro ' + unicode(self))
    self.completemacro(macro)

  def completemacro(self, macro):
    "Complete the macro with the parameters read."
    self.contents = [macro.instantiate()]
    for parameter in self.searchall(MacroParameter):
      index = parameter.number - 1
      parameter.contents = [self.values[index].clone()]

FormulaCommand.commandbits += [
    DefiningFunction(), MacroFunction(),
    ]

FormulaFactory.bits += [ MacroParameter() ]

class FormulaMacro(Formula):
  "A math macro defined in an inset."

  def __init__(self):
    self.parser = MacroParser()
    self.output = EmptyOutput()

  def __unicode__(self):
    "Return a printable representation."
    return 'Math macro'



class ContainerFactory(object):
  "Creates containers depending on the first line"

  def __init__(self):
    "Read table that convert start lines to containers"
    types = dict()
    for start, typename in ContainerConfig.starts.iteritems():
      types[start] = globals()[typename]
    self.tree = ParseTree(types)

  def createcontainer(self, reader):
    "Parse a single container."
    #Trace.debug('processing "' + reader.currentline().strip() + '"')
    if reader.currentline() == '':
      reader.nextline()
      return None
    type = self.tree.find(reader)
    container = type.__new__(type)
    container.__init__()
    container.start = reader.currentline().strip()
    self.parse(container, reader)
    return container

  def parse(self, container, reader):
    "Parse a container"
    parser = container.parser
    parser.parent = container
    parser.ending = self.getending(container)
    parser.factory = self
    container.header = parser.parseheader(reader)
    container.begin = parser.begin
    container.contents = parser.parse(reader)
    container.parameters = parser.parameters
    container.process()
    container.parser = None

  def getending(self, container):
    "Get the ending for a container"
    split = container.start.split()
    if len(split) == 0:
      return None
    start = split[0]
    if start in ContainerConfig.startendings:
      return ContainerConfig.startendings[start]
    classname = container.__class__.__name__
    if classname in ContainerConfig.endings:
      return ContainerConfig.endings[classname]
    if hasattr(container, 'ending'):
      Trace.error('Pending ending in ' + container.__class__.__name__)
      return container.ending
    return None

class ParseTree(object):
  "A parsing tree"

  default = '~~default~~'

  def __init__(self, types):
    "Create the parse tree"
    self.root = dict()
    for start, type in types.iteritems():
      self.addstart(type, start)

  def addstart(self, type, start):
    "Add a start piece to the tree"
    tree = self.root
    for piece in start.split():
      if not piece in tree:
        tree[piece] = dict()
      tree = tree[piece]
    if ParseTree.default in tree:
      Trace.error('Start ' + start + ' duplicated')
    tree[ParseTree.default] = type

  def find(self, reader):
    "Find the current sentence in the tree"
    branches = [self.root]
    for piece in reader.currentline().split():
      current = branches[-1]
      piece = piece.rstrip('>')
      if piece in current:
        branches.append(current[piece])
    while not ParseTree.default in branches[-1]:
      Trace.error('Line ' + reader.currentline().strip() + ' not found')
      branches.pop()
    last = branches[-1]
    return last[ParseTree.default]







class TOCEntry(Container):
  "A container for a TOC entry."

  copied = [StringContainer, Constant, Space]
  allowed = [
      TextFamily, EmphaticText, VersalitasText, BarredText,
      SizeText, ColorText, LangLine, Formula
      ]
  extracted = [
      PlainLayout, TaggedText, Align, Caption
      ]

  def header(self, container):
    "Create a TOC entry for header and footer (0 depth)."
    self.depth = 0
    self.output = EmptyOutput()
    return self

  def create(self, container):
    "Create the TOC entry for a container, consisting of a single link."
    self.entry = container.entry
    self.branches = []
    text = container.entry + ':'
    labels = container.searchall(Label)
    if len(labels) == 0 or Options.toc:
      url = Options.toctarget + '#toc-' + container.type + '-' + container.number
      link = Link().complete(text, url=url)
    else:
      label = labels[0]
      link = Link().complete(text)
      link.destination = label
    self.contents = [link]
    if container.number == '':
      link.contents.append(Constant(u' '))
    link.contents += self.gettitlecontents(container)
    self.output = TaggedOutput().settag('div class="toc"', True)
    if hasattr(container, 'level'):
      self.depth = container.level
    if hasattr(container, 'partkey'):
      self.partkey = container.partkey
    return self

  def gettitlecontents(self, container):
    "Get the title of the container."
    shorttitles = container.searchall(ShortTitle)
    if len(shorttitles) > 0:
      contents = [Constant(u' ')]
      for shorttitle in shorttitles:
        contents += shorttitle.contents
      return contents
    return self.safecontents(container)

  def safecontents(self, container):
    "Extract the safe contents for the TOC from a container."
    contents = []
    for element in container.contents:
      if element.__class__ in TOCEntry.copied:
        contents.append(element)
      elif element.__class__ in TOCEntry.allowed:
        contents.append(self.safeclone(element))
      elif element.__class__ in TOCEntry.extracted:
        contents += self.safecontents(element)
    return contents

  def safeclone(self, container):
    "Return a new container with contents only in a safe list, recursively."
    clone = Cloner.clone(container)
    clone.output = container.output
    clone.contents = self.safecontents(container)
    return clone

  def __unicode__(self):
    "Return a printable representation."
    return 'TOC entry: ' + self.entry

class Indenter(object):
  "Manages and writes indentation for the TOC."

  def __init__(self):
    self.depth = 0

  def getindent(self, depth):
    indent = ''
    if depth > self.depth:
      indent = self.openindent(depth - self.depth)
    elif depth < self.depth:
      indent = self.closeindent(self.depth - depth)
    self.depth = depth
    return Constant(indent)

  def openindent(self, times):
    "Open the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '<div class="tocindent">\n'
    return indent

  def closeindent(self, times):
    "Close the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '</div>\n'
    return indent

class TOCTree(object):
  "A tree that contains the full TOC."

  def __init__(self):
    self.tree = []
    self.branches = []

  def store(self, entry):
    "Place the entry in a tree of entries."
    while len(self.tree) < entry.depth:
      self.tree.append(None)
    if len(self.tree) > entry.depth:
      self.tree = self.tree[:entry.depth]
    stem = self.findstem()
    if len(self.tree) == 0:
      self.branches.append(entry)
    self.tree.append(entry)
    if stem:
      entry.stem = stem
      stem.branches.append(entry)

  def findstem(self):
    "Find the stem where our next element will be inserted."
    for element in reversed(self.tree):
      if element:
        return element
    return None

class TOCConverter(object):
  "A converter from containers to TOC entries."

  cache = dict()
  tree = TOCTree()

  def __init__(self):
    self.indenter = Indenter()

  def translate(self, container):
    "Translate a container to TOC entry + indentation."
    entry = self.convert(container)
    if not entry:
      return []
    indent = self.indenter.getindent(entry.depth)
    return [indent, entry]

  def convert(self, container):
    "Convert a container to a TOC entry."
    if container.__class__ in [LyXHeader, LyXFooter]:
      return TOCEntry().header(container)
    if not hasattr(container, 'partkey'):
      return None
    if container.partkey in self.cache:
      return TOCConverter.cache[container.partkey]
    if container.level > LyXHeader.tocdepth:
      return None
    entry = TOCEntry().create(container)
    TOCConverter.cache[container.partkey] = entry
    TOCConverter.tree.store(entry)
    return entry





import os.path


class Basket(object):
  "A basket to place a set of containers. Can write them, store them..."

  def setwriter(self, writer):
    self.writer = writer
    return self

class WriterBasket(Basket):
  "A writer of containers. Just writes them out to a writer."

  def write(self, container):
    "Write a container to the line writer."
    self.writer.write(container.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.close()

class KeeperBasket(Basket):
  "Keeps all containers stored."

  def __init__(self):
    self.contents = []

  def write(self, container):
    "Keep the container."
    self.contents.append(container)

  def finish(self):
    "Finish the basket by flushing to disk."
    self.flush()

  def flush(self):
    "Flush the contents to the writer."
    for container in self.contents:
      self.writer.write(container.gethtml())

class TOCBasket(Basket):
  "A basket to place the TOC of a document."

  def __init__(self):
    self.converter = TOCConverter()

  def setwriter(self, writer):
    Basket.setwriter(self, writer)
    Options.nocopy = True
    self.writer.write(LyXHeader().gethtml())
    return self

  def write(self, container):
    "Write the table of contents for a container."
    entries = self.converter.translate(container)
    for entry in entries:
      self.writer.write(entry.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.write(LyXFooter().gethtml())







class IntegralProcessor(object):
  "A processor for an integral document."

  def __init__(self):
    "Create the processor for the integral contents."
    self.storage = []

  def locate(self, container):
    "Locate only containers of the processed type."
    return isinstance(container, self.processedtype)

  def store(self, container):
    "Store a new container."
    self.storage.append(container)

  def process(self):
    "Process the whole storage."
    for container in self.storage:
      self.processeach(container)

class IntegralLayout(IntegralProcessor):
  "A processor for layouts that will appear in the TOC."

  processedtype = Layout
  tocentries = []

  def processeach(self, layout):
    "Keep only layouts that have an entry."
    if not hasattr(layout, 'entry'):
      return
    IntegralLayout.tocentries.append(layout)

class IntegralTOC(IntegralProcessor):
  "A processor for an integral TOC."

  processedtype = TableOfContents

  def processeach(self, toc):
    "Fill in a Table of Contents."
    toc.output = TaggedOutput().settag('div class="fulltoc"', True)
    converter = TOCConverter()
    for container in IntegralLayout.tocentries:
      toc.contents += converter.translate(container)
    # finish off with the footer to align indents
    toc.contents += converter.translate(LyXFooter())

  def writetotoc(self, entries, toc):
    "Write some entries to the TOC."
    for entry in entries:
      toc.contents.append(entry)

class IntegralBiblioEntry(IntegralProcessor):
  "A processor for an integral bibliography entry."

  processedtype = BiblioEntry

  def processeach(self, entry):
    "Process each entry."
    number = NumberGenerator.instance.generateunique('integralbib')
    link = Link().complete(number, 'biblio-' + number, type='biblioentry')
    entry.contents = [Constant('['), link, Constant('] ')]
    if entry.key in BiblioCite.cites:
      for cite in BiblioCite.cites[entry.key]:
        cite.complete(number, anchor = 'cite-' + number)
        cite.destination = link

class IntegralFloat(IntegralProcessor):
  "Store all floats in the document by type."

  processedtype = Float
  bytype = dict()

  def processeach(self, float):
    "Store each float by type."
    if not float.type in IntegralFloat.bytype:
      IntegralFloat.bytype[float.type] = []
    IntegralFloat.bytype[float.type].append(float)

class IntegralListOf(IntegralProcessor):
  "A processor for an integral list of floats."

  processedtype = ListOf

  def processeach(self, listof):
    "Fill in a list of floats."
    listof.output = TaggedOutput().settag('div class="fulltoc"', True)
    if not listof.type in IntegralFloat.bytype:
      Trace.message('No floats of type ' + listof.type)
      return
    for float in IntegralFloat.bytype[listof.type]:
      entry = self.processfloat(float)
      if entry:
        listof.contents.append(entry)

  def processfloat(self, float):
    "Get an entry for the list of floats."
    if float.parentfloat:
      return None
    return TOCEntry().create(float)

class IntegralReference(IntegralProcessor):
  "A processor for a reference to a label."

  processedtype = Reference

  def processeach(self, reference):
    "Extract the text of the original label."
    text = reference.destination.labelnumber
    if text:
      reference.labelnumber = text
      reference.format()

class MemoryBasket(KeeperBasket):
  "A basket which stores everything in memory, processes it and writes it."

  def __init__(self):
    "Create all processors in one go."
    KeeperBasket.__init__(self)
    self.processors = [
        IntegralLayout(), IntegralTOC(), IntegralBiblioEntry(),
        IntegralFloat(), IntegralListOf(), IntegralReference()
        ]

  def finish(self):
    "Process everything which cannot be done in one pass and write to disk."
    self.process()
    self.flush()

  def process(self):
    "Process everything with the integral processors."
    self.searchintegral()
    for processor in self.processors:
      processor.process()

  def searchintegral(self):
    "Search for all containers for all integral processors."
    for container in self.contents:
      # container.tree()
      if self.integrallocate(container):
        self.integralstore(container)
      container.locateprocess(self.integrallocate, self.integralstore)

  def integrallocate(self, container):
    "Locate all integrals."
    for processor in self.processors:
      if processor.locate(container):
        return True
    return False

  def integralstore(self, container):
    "Store a container in one or more processors."
    for processor in self.processors:
      if processor.locate(container):
        processor.store(container)







class SplitPartLink(IntegralProcessor):
  "A link processor for multi-page output."

  processedtype = Link

  def processeach(self, link):
    "Process each link and add the current page."
    link.page = self.page

class SplitPartHeader(object):
  "The header that comes with a new split page."

  upanchors = []
  prev = TranslationConfig.constants['prev']
  next = TranslationConfig.constants['next']
  up = TranslationConfig.constants['up']

  def __init__(self, firstbasket):
    "Set the first basket as last basket."
    self.lastcontainer = None
    self.nextlink = None
    firstbasket.write(self.insertupanchor())

  def create(self, basket, container):
    "Write the header to the basket."
    basket.write(LyXHeader())
    basket.write(self.createupanchor(container))
    basket.write(self.createheader(container))

  def createheader(self, container):
    "Create the header with all links."
    prevlink = Link().complete(' ', 'prev', type='prev')
    if self.nextlink:
      self.setlinkname(prevlink, SplitPartHeader.prev, self.lastcontainer)
      self.setlinkname(self.nextlink, SplitPartHeader.next, container)
      prevlink.setmutualdestination(self.nextlink)
    nextlink = Link().complete(' ', SplitPartHeader.next, type='next')
    uplink = Link().complete(SplitPartHeader.up, url='', type='up')
    uplink.destination = self.getupdestination(container)
    prevcontainer = TaggedText().complete([prevlink], 'span class="prev"')
    nextcontainer = TaggedText().complete([nextlink], 'span class="next"')
    upcontainer = TaggedText().complete([uplink], 'span class="up"')
    contents = [prevcontainer, Constant('\n'), upcontainer, Constant('\n'), nextcontainer]
    header = TaggedText().complete(contents, 'div class="splitheader"', True)
    self.nextlink = nextlink
    self.lastcontainer = container
    return header
  
  def createupanchor(self, container):
    "Create the up anchor for the up links."
    level = self.getlevel(container)
    while len(SplitPartHeader.upanchors) > level:
      del SplitPartHeader.upanchors[-1]
    while len(SplitPartHeader.upanchors) < level:
      SplitPartHeader.upanchors.append(SplitPartHeader.upanchors[-1])
    return self.insertupanchor()

  def insertupanchor(self):
    "Insert the up anchor into the list of anchors."
    upanchor = Link().complete('', '')
    upanchor.output = EmptyOutput()
    SplitPartHeader.upanchors.append(upanchor)
    return upanchor

  def getupdestination(self, container):
    "Get the name of the up page."
    level = self.getlevel(container)
    if len(SplitPartHeader.upanchors) < level:
      uppage = SplitPartHeader.upanchors[-1]
    else:
      uppage = SplitPartHeader.upanchors[level - 1]
    return uppage

  def getlevel(self, container):
    "Get the level of the container."
    if not hasattr(container, 'level'):
      return 1
    else:
      return container.level + 1

  def setlinkname(self, link, type, container):
    "Set the name on the link."
    if hasattr(container, 'mustsplit'):
      entry = container.mustsplit
    else:
      entry = container.entry
    link.contents = [Constant(type + ': ' + entry)]
  
class SplitPartBasket(Basket):
  "A basket used to split the output in different files."

  baskets = []

  def setwriter(self, writer):
    if not hasattr(writer, 'filename') or not writer.filename:
      Trace.error('Cannot use standard output for split output; ' +
          'please supply an output filename.')
      exit()
    self.writer = writer
    self.filename = writer.filename
    self.converter = TOCConverter()
    self.basket = MemoryBasket()
    self.basket.page = writer.filename
    return self

  def write(self, container):
    "Write a container, possibly splitting the file."
    self.basket.write(container)

  def finish(self):
    "Process the whole basket, create page baskets and flush all of them."
    self.basket.process()
    basket = self.firstbasket()
    header = SplitPartHeader(basket)
    for container in self.basket.contents:
      if self.mustsplit(container):
        filename = self.getfilename(container)
        Trace.debug('New page ' + filename)
        basket.write(LyXFooter())
        basket = self.addbasket(filename)
        header.create(basket, container)
      basket.write(container)
    for basket in self.baskets:
      basket.process()
    for basket in self.baskets:
      basket.flush()

  def firstbasket(self):
    "Create the first basket."
    return self.addbasket(self.filename, self.writer)

  def addbasket(self, filename, writer = None):
    "Add a new basket."
    if not writer:
      writer = LineWriter(filename)
    basket = MemoryBasket()
    basket.setwriter(writer)
    self.baskets.append(basket)
    # set the page name everywhere
    basket.page = filename
    splitpartlink = SplitPartLink()
    splitpartlink.page = os.path.basename(basket.page)
    basket.processors = [splitpartlink]
    return basket

  def mustsplit(self, container):
    "Find out if the oputput file has to be split at this entry."
    if self.splitalone(container):
      return True
    if not hasattr(container, 'entry'):
      return False
    entry = self.converter.convert(container)
    if not entry:
      return False
    return entry.depth <= Options.splitpart

  def splitalone(self, container):
    "Find out if the container must be split in its own page."
    found = []
    container.locateprocess(
        lambda container: container.__class__ in [PrintNomenclature, PrintIndex],
        lambda container: found.append(container.__class__.__name__))
    if not found:
      return False
    container.depth = 0
    container.mustsplit = found[0].lower().replace('print', '')
    return True

  def getfilename(self, container):
    "Get the new file name for a given container."
    if hasattr(container, 'mustsplit'):
      partname = container.mustsplit
    else:
      if container.level == Options.splitpart and container.number != '':
        partname = container.number
      else:
        if container.number == '':
          partname = container.partkey.replace('toc-', '').replace('*', '-')
        else:
          partname = container.type + '-' + container.number
    base, extension = os.path.splitext(self.filename)
    return base + '-' + partname + extension






class PostTable(object):
  "Postprocess a table"

  processedclass = Table

  def postprocess(self, last, table, next):
    "Postprocess a table: long table, multicolumn rows"
    self.longtable(table)
    for row in table.contents:
      index = 0
      while index < len(row.contents):
        self.checkforplain(row, index)
        self.checkmulticolumn(row, index)
        index += 1
    return table

  def longtable(self, table):
    "Postprocess a long table, removing unwanted rows"
    if not 'features' in table.parameters:
      return
    features = table.parameters['features']
    if not 'islongtable' in features:
      return
    if features['islongtable'] != 'true':
      return
    if self.hasrow(table, 'endfirsthead'):
      self.removerows(table, 'endhead')
    if self.hasrow(table, 'endlastfoot'):
      self.removerows(table, 'endfoot')

  def hasrow(self, table, attrname):
    "Find out if the table has a row of first heads"
    for row in table.contents:
      if attrname in row.parameters:
        return True
    return False

  def removerows(self, table, attrname):
    "Remove the head rows, since the table has first head rows."
    for row in table.contents:
      if attrname in row.parameters:
        row.output = EmptyOutput()

  def checkforplain(self, row, index):
    "Make plain layouts visible if necessary."
    cell = row.contents[index]
    plainlayouts = cell.searchall(PlainLayout)
    if len(plainlayouts) <= 1:
      return
    for plain in plainlayouts:
      plain.makevisible()

  def checkmulticolumn(self, row, index):
    "Process a multicolumn attribute"
    cell = row.contents[index]
    if not hasattr(cell, 'parameters') or not 'multicolumn' in cell.parameters:
      return
    mc = cell.parameters['multicolumn']
    if mc != '1':
      Trace.error('Unprocessed multicolumn=' + unicode(multicolumn) +
          ' cell ' + unicode(cell))
      return
    total = 1
    index += 1
    while self.checkbounds(row, index):
      del row.contents[index]
      total += 1
    cell.setmulticolumn(total)

  def checkbounds(self, row, index):
    "Check if the index is within bounds for the row"
    if index >= len(row.contents):
      return False
    if not 'multicolumn' in row.contents[index].parameters:
      return False
    if row.contents[index].parameters['multicolumn'] != '2':
      return False
    return True

Postprocessor.stages.append(PostTable)






class PostFormula(object):
  "Postprocess a formula"

  processedclass = Formula

  def postprocess(self, last, formula, next):
    "Postprocess any formulae"
    if Options.jsmath or Options.mathjax:
      return formula
    self.postnumbering(formula)
    self.postcontents(formula.contents)
    self.posttraverse(formula)
    return formula

  def postnumbering(self, formula):
    "Check if it's a numbered equation, insert number."
    if formula.header[0] != 'numbered':
      return
    functions = formula.searchremove(LabelFunction)
    if len(functions) == 0:
      label = self.createlabel(formula)
    elif len(functions) == 1:
      label = self.createlabel(formula, functions[0])
    if len(functions) <= 1:
      label.parent = formula
      formula.contents.insert(0, label)
      return
    for function in functions:
      label = self.createlabel(formula, function)
      row = self.searchrow(function)
      label.parent = row
      row.contents.insert(0, label)

  def createlabel(self, formula, function = None):
    "Create a new label for a formula."
    "Add a label to a formula."
    number = NumberGenerator.instance.generatechaptered('formula')
    entry = '(' + number + ')'
    if not hasattr(formula, number) or not formula.number:
      formula.number = number
      formula.entry = entry
    if not function:
      label = Label()
      label.create(entry + ' ', 'eq-' + number, type="eqnumber")
    else:
      label = function.label
      label.complete(entry + ' ')
    return label

  def searchrow(self, function):
    "Search for the row that contains the label function."
    if isinstance(function.parent, Formula) or isinstance(function.parent, FormulaRow):
      return function.parent
    return self.searchrow(function.parent)

  def postcontents(self, contents):
    "Search for sum or integral"
    for index, bit in enumerate(contents):
      self.checklimited(contents, index)
      if isinstance(bit, FormulaBit):
        self.postcontents(bit.contents)

  def checklimited(self, contents, index):
    "Check for a command with limits"
    bit = contents[index]
    if not isinstance(bit, EmptyCommand):
      return
    if not bit.command in FormulaConfig.limits['commands']:
      return
    limits = self.findlimits(contents, index + 1)
    limits.reverse()
    if len(limits) == 0:
      return
    tagged = TaggedBit().complete(limits, 'span class="limits"')
    contents.insert(index + 1, tagged)

  def findlimits(self, contents, index):
    "Find the limits for the command"
    limits = []
    while index < len(contents):
      if not self.checklimits(contents, index):
        return limits
      limits.append(contents[index])
      del contents[index]
    return limits

  def checklimits(self, contents, index):
    "Check for a command making the limits"
    bit = contents[index]
    if not isinstance(bit, SymbolFunction):
      return False
    if not bit.command in FormulaConfig.limits['operands']:
      return False
    bit.output.tag += ' class="bigsymbol"'
    return True

  def posttraverse(self, formula):
    "Traverse over the contents to alter variables and space units."
    flat = self.flatten(formula)
    last = None
    for bit, contents in self.traverse(flat):
      if bit.type == 'alpha':
        self.italicize(bit, contents)
      elif bit.type == 'font' and last and last.type == 'number':
        bit.contents.insert(0, FormulaConstant(u' '))
        # last.contents.append(FormulaConstant(u' '))
      last = bit

  def flatten(self, bit):
    "Return all bits as a single list of (bit, list) pairs."
    flat = []
    for element in bit.contents:
      if element.type:
        flat.append((element, bit.contents))
      elif isinstance(element, FormulaBit):
        flat += self.flatten(element)
    return flat

  def traverse(self, flattened):
    "Traverse each (bit, list) pairs of the formula."
    for element in flattened:
      yield element

  def italicize(self, bit, contents):
    "Italicize the given bit of text."
    index = contents.index(bit)
    contents[index] = TaggedBit().complete([bit], 'i')

Postprocessor.stages.append(PostFormula)



class eLyXerConverter(object):
  "Converter for a document in a lyx file. Places all output in a given basket."

  def __init__(self):
    self.filtering = False

  def setio(self, ioparser):
    "Set the InOutParser"
    self.reader = ioparser.getreader()
    self.basket = self.getbasket()
    self.basket.setwriter(ioparser.getwriter())
    return self

  def getbasket(self):
    "Get the appropriate basket for the current options."
    if Options.toc:
      return TOCBasket()
    if Options.splitpart:
      return SplitPartBasket()
    if Options.memory:
      return MemoryBasket()
    return WriterBasket()

  def embed(self, reader):
    "Embed the results from a reader into a memory basket."
    "Header and footer are ignored. Useful for embedding one document inside another."
    self.filtering = True
    self.reader = reader
    self.basket = MemoryBasket()
    self.writer = NullWriter()
    return self

  def convert(self):
    "Perform the conversion for the document"
    try:
      self.processcontents()
    except (Exception):
      version = '[eLyXer version ' + GeneralConfig.version['number']
      version += ' (' + GeneralConfig.version['date'] + ') in '
      version += Options.location + '] '
      Trace.error(version)
      Trace.error('Conversion failed at ' + self.reader.currentline())
      raise

  def processcontents(self):
    "Parse the contents and write it by containers"
    factory = ContainerFactory()
    self.postproc = Postprocessor()
    while not self.reader.finished():
      container = factory.createcontainer(self.reader)
      if container and not self.filtered(container):
        result = self.postproc.postprocess(container)
        if result:
          self.basket.write(result)
    # last round: clear the pipeline
    result = self.postproc.postprocess(None)
    if result:
      self.basket.write(result)
    if not self.filtering:
      self.basket.finish()

  def filtered(self, container):
    "Find out if the container is a header or footer and must be filtered."
    if not self.filtering:
      return False
    if container.__class__ in [LyXHeader, LyXFooter]:
      return True
    return False

  def getcontents(self):
    "Return the contents of the basket."
    return self.basket.contents

  def __unicode__(self):
    "Printable representation."
    string = 'Converter with filtering ' + unicode(self.filtering)
    string += ' and basket ' + unicode(self.basket)
    return string

class InOutParser(object):
  "Parse in and out arguments"

  def __init__(self):
    self.filein = sys.stdin
    self.fileout = sys.stdout

  def parse(self, args):
    "Parse command line arguments"
    self.filein = sys.stdin
    self.fileout = sys.stdout
    if len(args) < 2:
      Trace.quietmode = True
    if len(args) > 0:
      self.filein = args[0]
      del args[0]
      self.readdir(self.filein, 'directory')
    else:
      Options.directory = '.'
    if len(args) > 0:
      self.fileout = args[0]
      del args[0]
      self.readdir(self.fileout, 'destdirectory')
    else:
      Options.destdirectory = '.'
    if len(args) > 0:
      raise Exception('Unused arguments: ' + unicode(args))
    return self

  def getreader(self):
    "Get the resulting reader."
    return LineReader(self.filein)

  def getwriter(self):
    "Get the resulting writer."
    return LineWriter(self.fileout)

  def readdir(self, filename, diroption):
    "Read the current directory if needed"
    if getattr(Options, diroption) != None:
      return
    setattr(Options, diroption, os.path.dirname(filename))
    if getattr(Options, diroption) == '':
      setattr(Options, diroption, '.')

class NullWriter(object):
  "A writer that goes nowhere."

  def write(self, list):
    "Do nothing."
    pass

class ConverterFactory(object):
  "Create a converter fit for converting a filename and embedding the result."

  def create(self, container):
    "Create a converter for a given container, with filename"
    " and possibly other parameters."
    fullname = os.path.join(Options.directory, container.filename)
    reader = LineReader(container.filename)
    if 'firstline' in container.lstparams:
      reader.setstart(int(container.lstparams['firstline']))
    if 'lastline' in container.lstparams:
      reader.setend(int(container.lstparams['lastline']))
    return eLyXerConverter().embed(reader)

IncludeInset.converterfactory = ConverterFactory()



def convertdoc(args):
  "Read a whole document and write it"
  Options().parseoptions(args)
  ioparser = InOutParser().parse(args)
  converter = eLyXerConverter().setio(ioparser)
  converter.convert()

def main():
  "Main function, called if invoked from the command line"
  convertdoc(list(sys.argv))

if __name__ == '__main__':
  main()

