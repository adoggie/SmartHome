#coding:utf-8

from box import BoxController
from mantis.fundamental.parser.yamlparser import YamlConfigParser

def main():
    parser = YamlConfigParser('./settings.yaml')
    BoxController().init(parser.props)

if __name__=='__main__':
    main()