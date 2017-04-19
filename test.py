# -*- coding: UTF-8 -*-

raw_type_dict = {
    "耕地": ["水田", "旱地"],
    "园地": ["果园", "茶园"]
}
type_dict = {}


def create_type_dict(raw_dict):
    return {child: prt for prt in raw_dict.keys() for child in raw_dict[prt]}

type_dict = create_type_dict(raw_type_dict)

for k, v in type_dict.items():
    print k, v
