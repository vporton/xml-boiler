#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
from typing import NamedTuple

from dependency_injector.providers import ThreadLocalSingleton
from dependency_injector.containers import DeclarativeContainer
from rdflib import URIRef

from xmlboiler.core.rdf_format.base import MAIN_NAMESPACE
from xmlboiler.core.rdf_recursive_descent.base import NodeParser, ErrorHandler
from xmlboiler.core.rdf_recursive_descent.compound import Choice, ZeroOnePredicate, OnePredicate
from xmlboiler.core.rdf_recursive_descent.enum import EnumParser
from xmlboiler.core.rdf_format.asset import AssetInfo, TransformerKindEnum, ValidatorKindEnum, BaseScriptInfo, \
    ScriptKindEnum, ScriptInfo, CommandScriptInfo
from xmlboiler.core.rdf_recursive_descent.list import ListParser
from xmlboiler.core.rdf_recursive_descent.literal import FloatLiteral, StringLiteral, IRILiteral
from xmlboiler.core.rdf_recursive_descent.types import check_node_class


class ScriptInfoParser(Choice):
    def __init__(self, transformer, subclasses, script_kind: ScriptKindEnum):
        # Intentionally not using dependency injection pattern
        super().__init__([CommandScriptInfoParser   (transformer, subclasses, script_kind),
                          WebServiceScriptInfoParser(transformer, subclasses, script_kind)])
        # self.subclasses = subclasses
        # self.script_kind = script_kind

    # def parse(self, parse_context, graph, node):


class _AttributeParamParser(NodeParser):
    def parse(self, parse_context, graph, node):
        return OnePredicate(URIRef(MAIN_NAMESPACE + "attribute"), _ParamAttributeParser(), ErrorHandler.WARNING).parse(parse_context, graph, node)


class _ParamParser(NodeParser):
    def parse(self, parse_context, graph, node):
        name = OnePredicate(URIRef(MAIN_NAMESPACE + "name"), StringLiteral(ErrorHandler.IGNORE), ErrorHandler.WARNING).\
            parse(parse_context, graph, node)
        value = OnePredicate(URIRef(MAIN_NAMESPACE + "value"),
                             Choice([StringLiteral(ErrorHandler.IGNORE), _AttributeParamParser()]),
                             ErrorHandler.WARNING).\
            parse(parse_context, graph, node)
        return (name, value)


class AttributeParam(NamedTuple):
    ns: URIRef
    name: str

class _ParamAttributeParser(NodeParser):
    def parse(self, parse_context, graph, node):
        ns = OnePredicate(URIRef(MAIN_NAMESPACE + "NS"), IRILiteral(ErrorHandler.WARNING), ErrorHandler.WARNING).\
            parse(parse_context, graph, node)
        name = OnePredicate(URIRef(MAIN_NAMESPACE + "name"), StringLiteral(ErrorHandler.WARNING), ErrorHandler.WARNING).\
            parse(parse_context, graph, node)
        return AttributeParam(ns, name)


class BaseScriptInfoParser(NodeParser):
    def __init__(self, transformer, script_kind):
        self.transformer = transformer
        self.script_kind = script_kind

    @staticmethod
    def create_transformer_kind_parser():
        map = {MAIN_NAMESPACE + "entire": TransformerKindEnum.ENTIRE,
               MAIN_NAMESPACE + "simpleSequential": TransformerKindEnum.SIMPLE_SEQUENTIAL,
               MAIN_NAMESPACE + "subdocumentSequential": TransformerKindEnum.SUBDOCUMENT_SEQUENTIAL,
               MAIN_NAMESPACE + "downUp": TransformerKindEnum.DOWN_UP,
               MAIN_NAMESPACE + "plainText": TransformerKindEnum.PLAIN_TEXT}
        return EnumParser(map)

    @staticmethod
    def create_validator_kind_parser():
        map = {MAIN_NAMESPACE + "entire": ValidatorKindEnum.ENTIRE,
               MAIN_NAMESPACE + "parts": ValidatorKindEnum.PARTS}
        return EnumParser(map)

    def parse(self, parse_context, graph, node):
        result = BaseScriptInfo(transformer=self.transformer, script_kind=self.script_kind)
        # TODO: Check 0..1 range
        float_parser = FloatLiteral(ErrorHandler.WARNING)
        preservance_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "preservance"),
                                              float_parser,
                                              1.0,
                                              ErrorHandler.WARNING)
        stability_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "stability"),
                                            float_parser,
                                            1.0,
                                            ErrorHandler.WARNING)
        preference_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "preference"),
                                             float_parser,
                                             1.0,
                                             ErrorHandler.WARNING)
        result.preservance = preservance_parser.parse(parse_context, graph, node)
        result.stability   = stability_parser.parse  (parse_context, graph, node)
        result.preference  = preference_parser.parse (parse_context, graph, node)
        if self.script_kind == ScriptKindEnum.TRANSFORMER:
            transformer_kind_parser = OnePredicate(URIRef(MAIN_NAMESPACE + "transformerKind"),
                                                   Providers.transformer_kind_parser(),
                                                   ErrorHandler.WARNING)
            result.transformer_kind = transformer_kind_parser.parse(parse_context, graph, node)
        elif self.script_kind == ScriptKindEnum.VALIDATOR:
            result.validator_kind = Providers.validator_kind_parser().parse(parse_context, graph, node)
        ok_result_node_parser = StringLiteral(ErrorHandler.WARNING)
        ok_result_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "okResult"),
                                            ok_result_node_parser,
                                            ErrorHandler.WARNING)
        result.ok_result = ok_result_parser.parse(parse_context, graph, node)
        return result


class CommandScriptInfoParser(NodeParser):
    def __init__(self, transformer, subclasses, script_kind):
        self.transformer = transformer
        self.subclasses = subclasses
        self.script_kind = script_kind

    def parse(self, parse_context, graph, node):
        klass = URIRef(MAIN_NAMESPACE + "Command")
        check_node_class(self.subclasses, parse_context, graph, node, klass, ErrorHandler.IGNORE)

        base = BaseScriptInfoParser(self.transformer, self.script_kind).parse(parse_context, graph, node)
        more = CommandScriptInfo()

        str1_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "scriptURL"), IRILiteral(ErrorHandler.WARNING), ErrorHandler.WARNING)
        str1 = str1_parser.parse(parse_context, graph, node)
        str2_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "commandString"), StringLiteral(ErrorHandler.WARNING), ErrorHandler.WARNING)
        str2 = str2_parser.parse(parse_context, graph, node)
        # if str1 is None and str2 is None:
        #     msg = parse_context.translate("Both :scriptURL and :commandString can't be missing in node {node}.").format(node=node)
        #     parse_context.throw(ErrorHandler.WARNING, msg)
        if str1 is not None and str2 is not None:
            msg = parse_context.translate("Both :scriptURL and :commandString can't be present in node {node}.").format(node=node)
            parse_context.throw(ErrorHandler.WARNING, msg)
        more.script_url     = str1
        more.command_string = str2

        if not more.script_url and len(more.params) != 0:
            def s():
                return parse_context.translate("Cannot provide params for commandString script {node}.").\
                    format(node=node)
            parse_context.throw(ErrorHandler.FATAL, s)

        min_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "minVersion"), StringLiteral(ErrorHandler.WARNING), ErrorHandler.WARNING)
        more.min_version = min_parser.parse(parse_context, graph, node)
        max_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "maxVersion"), StringLiteral(ErrorHandler.WARNING), ErrorHandler.WARNING)
        more.max_version = max_parser.parse(parse_context, graph, node)

        language_parser = OnePredicate(URIRef(MAIN_NAMESPACE + "language"), IRILiteral(ErrorHandler.WARNING), ErrorHandler.WARNING)
        more.language = language_parser.parse(parse_context, graph, node)

        params_parser = ZeroOnePredicate(URIRef(MAIN_NAMESPACE + "params"),
                                         ListParser(_ParamParser(), ErrorHandler.FATAL),
                                         ErrorHandler.WARNING,
                                         default_value=[])
        more.params = params_parser.parse(parse_context, graph, node)

        return ScriptInfo(base=base, more=more)


class WebServiceScriptInfoParser(NodeParser):
    def __init__(self, transformer, subclasses, script_kind):
        self.transformer = transformer
        self.subclasses = subclasses
        self.script_kind = script_kind

    def parse(self, parse_context, graph, node):
        klass = URIRef(MAIN_NAMESPACE + "WebService")
        check_node_class(self.subclasses, parse_context, graph, node, klass, ErrorHandler.IGNORE)

        base = BaseScriptInfoParser(self.transformer, self.script_kind).parse(parse_context, graph, node)
        more = CommandScriptInfo()

        action_parser = OnePredicate(URIRef(MAIN_NAMESPACE + "action"), IRILiteral(ErrorHandler.WARNING))
        more.action = action_parser.parse(parse_context, graph, node)
        method_parser = OnePredicate(URIRef(MAIN_NAMESPACE + "method"), IRILiteral(ErrorHandler.WARNING))
        more.method = method_parser.parse(parse_context, graph, node)
        xml_field_parser = OnePredicate(URIRef(MAIN_NAMESPACE + "xmlField"), IRILiteral(ErrorHandler.WARNING))
        more.xml_field = xml_field_parser.parse(parse_context, graph, node)

        return ScriptInfo(base=base, more=more)


class Providers(DeclarativeContainer):
    # What is more efficient: thread-local or thread-safe?
    transformer_kind_parser = ThreadLocalSingleton(BaseScriptInfoParser.create_transformer_kind_parser)
    validator_kind_parser   = ThreadLocalSingleton(BaseScriptInfoParser.create_validator_kind_parser  )
