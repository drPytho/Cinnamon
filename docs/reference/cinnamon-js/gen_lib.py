# coding: utf-8
# Dear future self,
#
# You're looking at this file because
# the parse function finally broke.
#
# It's not fixable. You have to rewrite it.
# Sincerely, past self
#
# Also, it's probably at least
# 2013. Did you ever take
# that trip to Iceland?

import re

class JSThing():
    def append_description(self, desc):
        if len(desc) == 0:
            self.description += "\n"
        else:
            self.description += ' ' + desc.strip().replace('<', '&lt;').replace('>', '&gt;')

    def get_xml_description(self):
        return re.sub('@(\w*)', '<code>\g<1></code>', "".join("<para>{0}</para>".format(x) for x in self.description.split("\n")))

    def add_property(self, prop):
        if prop.name == "short_description":
            self.short_description = prop.description
        else:
            self.properties.append(prop)

class JSFunction(JSThing):
    def __init__ (self, name):
        self.name = name
        self.description = ''
        self.short_description = ''
        self.properties = []
        self.return_value = JSProperty(None, '', '')

    def add_function(self, func):
        self.functions.append(func)

    def set_return(self, retval):
        self.return_value = retval

class JSProperty(JSThing):
    def __init__ (self, name, arg_type, desc):
        self.name = name
        self.arg_type = arg_type if arg_type else ''
        self.description = ''
        self.append_description(desc)

    def get_type_link(self):
        from gen_doc import objects

        if self.arg_type == '':
            return "void"
        else:
            if self.arg_type in objects:
                return "cinnamon-js-" + objects[self.arg_type].prefix
            else:
                return self.arg_type.replace('.', '')

class JSFile(JSThing):
    def __init__ (self, directory, name):
        self.directory = directory
        self.name = name[0].capitalize() + name[1:]
        self.imports = "imports.{0}.{1}".format(directory, name)
        self.prefix = directory + "-" + name
        self.description = ''
        self.short_description = ''
        self.properties = []
        self.objects = []
        self.functions = []

    def is_interesting(self):
        return len(self.functions) + len(self.properties) + len(self.description) > 0

    def add_function(self, func):
        self.functions.append(func) 

    def add_object(self, obj):
        self.objects.append(obj)
        obj.parent = self
        obj.directory = self.directory
        obj.prefix = self.prefix + "-" + obj.name
        obj.name = self.name + "-" + obj.name

class JSObject(JSThing):
    def __init__ (self, name):
        self.name = name
        self.inherit = ''
        self.description = ''
        self.short_description = ''
        self.parent = None
        self.directory = None
        self.prefix = None
        self.functions = []
        self.properties = []

    def add_function(self, func):
        self.functions.append(func)

    def set_inherit(self, inherit):
        self.inherit = inherit

def write_sgml(files, version):
    sgml = open('cinnamon-js-docs.sgml', 'w')
    sgml.write('''<?xml version='1.0'?>
<!DOCTYPE book PUBLIC '-//OASIS//DTD DocBook XML V4.3//EN'
               'http://www.oasis-open.org/docbook/xml/4.3/docbookx.dtd'
[
  <!ENTITY % local.common.attrib "xmlns:xi  CDATA  #FIXED 'http://www.w3.org/2003/XInclude'">
]>
<book id='index'>
  <bookinfo>
    <title>Cinnamon Javascript Reference Manual</title>
    <releaseinfo>
      for Cinnamon {0}.
    </releaseinfo>
  </bookinfo>
'''.format(version))

    f = open('tutorials.xml', 'r')
    sgml.write(f.read())

    sgml.write('''
  <part id="cinnamon-js-reference">
    <title>Cinnamon Javascript Reference</title>''')

    for _file in files:
        if not _file.is_interesting() and len(_file.objects) == 0:
            continue

        sgml.write('''
  <chapter id="cinnamon-js-{0}-section">
    <title>{1}</title>
'''.format(_file.prefix, _file.imports))
        if _file.is_interesting():
            sgml.write('    <xi:include href="{0}/{1}.xml"/>\n'.format(_file.directory, _file.name));

        for obj in _file.objects:
            sgml.write('    <xi:include href="{0}/{1}.xml"/>\n'.format(_file.directory, obj.name));

        sgml.write('  </chapter>\n\n')

    sgml.write('</part></book>\n')


def create_file(obj):
    file_obj = open('{0}/{1}.xml'.format(obj.directory, obj.name), 'w')
    file_obj.write('''<?xml version='1.0'?>
<!DOCTYPE refentry PUBLIC '-//OASIS//DTD DocBook XML V4.3//EN'
'http://www.oasis-open.org/docbook/xml/4.3/docbookx.dtd'
[
<!ENTITY % local.common.attrib "xmlns:xi  CDATA  #FIXED 'http://www.w3.org/2003/XInclude'">
]>
<refentry id="cinnamon-js-{0}">
  <refmeta>
    <refentrytitle role="top_of_page" id="cinnamon-js-{0}.top_of_page">{1}</refentrytitle>
    <manvolnum>3</manvolnum>
    <refmiscinfo>
      {1}
    </refmiscinfo>
  </refmeta>
  <refnamediv>
    <refname>{1}</refname>
    <refpurpose>{2}</refpurpose>
  </refnamediv>
'''.format(obj.prefix, obj.name.replace("-", "."), obj.short_description))

    return file_obj

def write_function_header_block(file_obj, obj):
    if len(obj.functions) == 0:
        return;

    file_obj.write('''
  <refsect1 id="cinnamon-js-{0}.functions" role="functions_proto">
    <title role="functions_proto.title">Functions</title>
    <informaltable pgwide="1" frame="none">
      <tgroup cols="2">
        <colspec colname="functions_return" colwidth="150px"/>
        <colspec colname="functions_name"/>
        <tbody>'''.format(obj.prefix))

    for func in obj.functions:
        file_obj.write('''
          <row>
            <entry role="function_type">
              <link linkend="{0}">
                <returnvalue>{1}</returnvalue>
              </link>
            </entry>
            <entry role="function_name">
              <link linkend="cinnamon-js-{2}-{3}">{3}</link>&#160;<phrase role="c_punctuation">()</phrase>
            </entry>
          </row>'''.format(func.return_value.get_type_link(), func.return_value.arg_type, obj.prefix, func.name))
    file_obj.write('''
        </tbody>
      </tgroup>
    </informaltable>
  </refsect1>''')

def write_properties_header_block(file_obj, obj):
    if len(obj.properties) == 0:
        return

    file_obj.write('''
  <refsect1 id="Cinnamon-js-{0}.properties" role="properties">
    <title role="properties.title">Properties</title>
    <informaltable frame="none">
      <tgroup cols="3">
        <colspec colname="properties_type" colwidth="150px"/>
        <colspec colname="properties_name" colwidth="300px"/>
        <tbody>'''.format(obj.prefix))

    for prop in obj.properties:
        file_obj.write('''
          <row>
            <entry role="property_type">
              <link linkend="{0}"><type>{1}</type></link>
            </entry>
            <entry role="property_name">
              <link linkend="cinnamon-js-{2}--{3}">{3}</link>
            </entry>
          </row>'''.format(prop.get_type_link(), prop.arg_type, obj.prefix, prop.name));
    file_obj.write('''
        </tbody>
      </tgroup>
    </informaltable>
  </refsect1>''')

def write_heirarchy_block(file_obj, obj):
    from gen_doc import objects

    name = obj.name.replace('-', '.')
    heirarchy = []
    try:
        while True:
            name = objects[name].inherit
            if name in heirarchy:
                break
            if name:
                heirarchy.insert(0, name)
    except KeyError:
        pass

    file_obj.write('''
  <refsect1 id="cinnamon-js-{0}.object-hierarchy" role="object_hierarchy">
    <title role="object_hierarchy.title">Object Hierarchy</title>
    <screen>
      <link linkend="Object">Object</link>'''.format(obj.prefix))
    count = 0
    for item in heirarchy:
        try:
            file_obj.write('''
{0}<phrase role="lineart">&#9584;&#9472;&#9472;</phrase> <link linkend="cinnamon-js-{1}">{2}</link>'''.format(' ' * (count * 4 + 6), objects[item].prefix, item))
        except KeyError:
            file_obj.write('''
{0}<phrase role="lineart">&#9584;&#9472;&#9472;</phrase>{1}'''.format(' ' * (count * 4 + 6), item))
        count += 1

    file_obj.write('''
{0}<phrase role="lineart">&#9584;&#9472;&#9472;</phrase> {1}'''.format(' ' * (count * 4 + 6), obj.name.replace("-", ".")))
    file_obj.write('''
    </screen>
  </refsect1>''')

def write_description_block(file_obj, obj):
    if len(obj.description) == 0:
        return
    
    file_obj.write('''
  <refsect1 id="cinnamon-js-{0}.description" role="desc">
    <title role="desc.title">Description</title>
    {1}
  </refsect1>'''.format(obj.prefix, obj.get_xml_description()))

def write_functions_block(file_obj, obj):
    if len(obj.functions) == 0:
        return

    file_obj.write('''
  <refsect1 id="cinnamon-js-{0}.functions_details" role="details">
    <title role="details.title">Functions</title>'''.format(obj.prefix))
    for func in obj.functions:
        file_obj.write('''
    <refsect2 id="cinnamon-js-{0}-{1}" role="function">
      <title>{1}&#160;()</title>
      <indexterm zone="cinnamon-js-{0}-{1}"><primary>{1}</primary></indexterm>
      <programlisting language="javascript">
<link linkend="{2}"><returnvalue>{3}</returnvalue></link>
'''.format(
            obj.prefix,
            func.name,
            func.return_value.get_type_link(),
            func.return_value.arg_type))

        file_obj.write(func.name + " (")
        if len(func.properties) > 0:
            max_length = max(len(x.arg_type) for x in func.properties) + 3
            # If no parameter has argument types, don't show that silly whitespace
            if max_length == 3:
                max_length = 0

            file_obj.write((',\n' + ' ' * (len(func.name) + 2)).join(
                '<parameter><link linkend="{0}"><type>{1}</type></link>{2}</parameter>'.format(
                    x.get_type_link(),
                    x.arg_type,
                    " " * (max_length - len(x.arg_type)) + x.name) for x in func.properties))
        file_obj.write(');</programlisting>\n')
       
        file_obj.write(func.get_xml_description())

        if len(func.properties) > 0:
            file_obj.write('''
      <refsect3 role="parameters">
        <title>Parameters</title>
        <informaltable role="parameters_table" pgwide="1" frame="none">
          <tgroup cols="3">
            <colspec colname="parameters_name" colwidth="150px"/>
            <colspec colname="parameters_description"/>
            <colspec colname="parameters_annotations" colwidth="200px"/>
            <tbody>''')

            for prop in func.properties:
                file_obj.write('''
              <row><entry role="parameter_name"><para>{0}</para></entry>
                <entry role="parameter_description"><para>{1}</para></entry>
                <entry role="parameter_annotations"></entry></row>'''.format(prop.name, prop.description))
            file_obj.write('''
        </tbody></tgroup></informaltable>
      </refsect3>''')

        if func.return_value.name is not None:
            file_obj.write('<refsect3 role="returns"><title>Returns</title>{0}</refsect3>'.format(func.return_value.get_xml_description()))


        file_obj.write('''\n</refsect2>''')

    file_obj.write('\n  </refsect1>');

def write_properties_block(file_obj, obj):
    if len(obj.properties) == 0:
        return

    file_obj.write('''
  <refsect1 id="cinnamon-js-{0}.property-details" role="property_details">
    <title role="property_details.title">Property Details</title>'''.format(obj.prefix))

    for prop in obj.properties:
        file_obj.write('''
    <refsect2 id="cinnamon-js-{0}--{1}" role="property">
      <title>
      The “{1}” property
      </title>
      <indexterm zone="cinnamon-js-{0}--{1}">
        <primary>cinnamon-js-{0}:{1}</primary>
      </indexterm>
      <programlisting language="javascript">  {2}  <link linkend="{3}"><type>{4}</type></link></programlisting>
      {5}
    </refsect2>'''.format(
        obj.prefix,
        prop.name,
        ('“' + prop.name + '”').ljust(25),
        prop.get_type_link(),
        prop.arg_type, 
        prop.get_xml_description()))
    file_obj.write('''\n  </refsect1>''')

def close_file(file_obj):
    file_obj.write('''</refentry>''')
    file_obj.close()


