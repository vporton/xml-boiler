**[Program homepage](https://mathematics21.org/xml-boiler-software-automatic-transformation-of-xml-namespaces/)**

Automatically transform between XML namespaces.

https://en.wikiversity.org/wiki/Automatic_transformation_of_XML_namespaces

This is an alpha. It is already useful to process XInclude, XML comments,
and some home-made XHTML extensions.

See https://vporton.github.io/xml-boiler-docs/ for help.

This project supersedes failed project
https://github.com/vporton/xml-boiler-java

==

The following organizations were asked to support this project:
* Linux Foundation (2017 Nov 1)
* Free Software Foundation (2017 Nov 1) [they don't provide funding]
* http://www.osc.dial.community (2017 Nov 7)

# Project description #

## Overview ##

It was written a specification (draft but already "functional") for automatic transformation and validation of complex (possibly multi-namespace) XML documents based on namespaces, written a software (XML Boiler) to implement these transformations. Written a short tutorial for XML Boiler.

Most of the specification was implemented in Python programming language. This project prototype "XML Boiler" is already nearly complete and is practically useful.

The most high priority current project goal is to rewrite the entire project in D programming language (because Python was found too slow and also not enough reliable).

Also we need better validation support and more transformers/validators need to be written, as well as many more features to implement. The specification needs to be improved to reach non-draft state.

Additional project purpose: Develop some general purpose (foundational) libraries for D programming language.

The benefits of the project include:

* freely intermix tag sets of different sets of tag semantics (using XML namespaces), without disturbing each other (such as by name clash) in the global world

* add your new tags to HTML (and other XML-based formats)

   * get rid of using HTML in the future Web, switch it to proper semantic XML formats

     * make XSL-format based browsers with automatic generation of XSL from other XML formats

   * make automatic coloring of source listings (for example)

* add macroses and include (such as by XInclude) other files in XML

* intermix different XML formats, with intelligent automatic processing of the mix

  * embed one XML format in another one

  * automatically choose the order of different XML converters applied to your mixed XML file

* make browsers to show your XML in arbitrary format

* make processing XML intelligent (with your custom scripts), both on the level of scripts and on the level of interactions between scripts

* integrating together XML conversion and validation scripts written in multiple programming languages

* associating semantics (such as relations with other namespaces and validation rules) to a namespace

  * semantics can be described as an RDF resource at a namespace URL (or a related URL)

* many more opportunities

* integrate all of the above in single command

## Intellectual Merit ##

There was no automatic way to transform between XML files of different formats previously. This new way is a technological revolution. The same concerns validation of multi-namespace XML documents.

The main author’s invention is an elaborate automatic selection of the order (with repetitions if needed) of the XML transformations apply to the transformed XML file or its parts (processing of XML file by parts is also an author’s invention).

The project’s philosophical value is assigning semantics to XML namespaces, mainly as interrelations between different namespaces, what was previously considered like something non-existing.

The specification written is a breakthrough in XML processing. Many details were needed to be resolved in a clever way when writing it.

The D language is considered by the author as the currently most advanced and perspective programming language, thus making the purpose to advance D libraries important.
Broader Impacts
The project intends to replace older means such as HTML and TeX/LaTeX, so revolutionizing such things as the Web and scientific writing.

A future HTML replacement could be done in practice in the following steps:

1. Develop some tag sets by independent users or standardization committees. Use my software to convert XML files containing them to usual HTML for legacy browser compatibility.

2. Standardize news tag sets as a part of a new post-HTML standard(s).

3. Support the new tags sets in browsers (and other HTML software such as search engines).
This would provide a smooth, multi-stage transition from legacy HTML to a new standard, what is before was impossible due to complexity of this global social process not being split into appropriate multiple stages, not allowing public participation of persons outside central standardization committees and smooth transition to new standards while the browsers are not yet updated (the chicken-egg problem: we were unable to update browsers while the standards are not yet updated and unable to update standards while the browsers are not yet updated, and also the need to do all the work in a central standardization committee not allowing enough public participation in developing a future HTML replacement).

Future TeX/LaTeX replacement could be done by developing a tag set (possibly including MathML for math formulas) for formatting complex “scientific” documents together with tag set(s) for complex Turing-complete logic (for such things as macroses and conditional processing, etc.) like one of TeX but much more convenient for the users and for transformation and data extraction software. Then this software could be optionally (partially) standardized. Unlike the above proposal of replacing HTML, for the TeX replacement it is not strictly necessary to create a browser software supporting it, but my software (together with scripts for it by other users) could itself be used as a TeX/LaTeX replacement. Then software for data transformation/extraction for databases like Scopus could be developed.

In the future RDF documents describing semantics of namespaces could be placed at namespace URLs (or related URLs) to support for anybody to be able to create and distribute his own XML tag sets standards and their semantics, without the need to resort to central standardization committees. (Scripts referred from such RDF documents could be executed in secure software sandboxes.)

The project files (including the documentation and study materials) are openly disseminated to the public, including by the means of Wikiversity study and research site.

The project improves Internet democracy and broader participation of underrepresented groups by allowing anyone to create his own XML standards.

The project develops free software: both specialized software for XML processing and general purpose software libraries.
