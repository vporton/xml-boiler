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

Written a specification (congratulate me with great work) for automatic transformation of XML documents based on namespaces, written a software (XML Boiler) to implement these transformations. Written a short tutorial for XML Boiler. 

There was no automatic way to transform between XML files of different formats previously. This new way is a technological revolution.

Most of the specification was implemented in Python programming language, resulting in this free software.

The most important current project goal (as of Apr 2019) is to rewrite the entire project in D programming language (because Python was found too slow and also not enough reliable).

Additional project purpose: Develop some general purpose libraries for D programming language.

The benefits of the project include:

* freely intermix tag sets of different sets of tag semantics (using XML namespaces), without disturbing each other (such as by name clash) in the global world

* add your new tags to HTML (and other XML-based formats)

  * get rid of using HTML in future Web, switch it to proper semantic XML formats

    * make XSL-format based browsers with automatic generation of XSL from other XML formats

  * make automatic coloring of source listings (for example)

* add macroses and include (such as by XInclude) other files in XML

* intermix different XML formats, with intelligent automatic processing of the mix

  * embed one XML format in another one

  * automatically choose the order of different XML converters applied to your mixed XML file

* make browsers to show your XML in arbitrary format

* make processing XML intelligent (with your custom scripts)

* integrating together XML conversion and validation scripts written in multiple programming languages

* associating semantics (such as relations with other namespaces and validation rules) to a namespace

  * semantics can be described as an RDF resource at a namespace URL (or a related URL)

* many more opportunities

* integrate all of the above in single command
