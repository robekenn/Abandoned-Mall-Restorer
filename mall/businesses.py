"""Opposite-court businesses and their owners, in reopening order."""
OPPOSITE = {
 'north': [('Corner Bakery',1000,22,'cafe','Pip','bread baskets'),('Bright Buttons',1400,30,'bookshop','Jo','button tins'),
           ('Paper Trails',1900,40,'bookshop','Finn','stationery sets'),('Orchard Cafe',2500,52,'cafe','Lena','fruit crates'),
           ('The Clock Shop',3200,65,'bookshop','Ash','clock parts')],
 'east': [('Needle & Note',10000,90,'bookshop','Sage','music books'),('Sunroom Tea',13000,115,'cafe','May','tea cups'),
          ('Pocket Wonders',16000,145,'bookshop','Lou','toy boxes'),('Silver Screen',20000,180,'bookshop','Ren','film reels'),
          ('Evening Market',25000,220,'cafe','Vic','market baskets')],
 'garden': [('Bloom & Brush',32000,220,'bookshop','Dawn','paint sets'),('The Potting Shed',39000,270,'bookshop','Reed','clay pots'),
            ('Harvest Counter',47000,330,'cafe','Bess','harvest crates'),('Woven Days',56000,400,'bookshop','Tess','woven cloth'),
            ('Wildflower House',66000,480,'bookshop','Flora','flower bundles')],
 'commons': [('Hearth & Honey',90000,490,'cafe','Owen','honey jars'),('Story Circle',107000,580,'bookshop','Noa','story collections'),
             ('Handmade Home',126000,680,'bookshop','Mina','handmade gifts'),('Morning Chorus',148000,800,'cafe','Arlo','breakfast trays'),
             ('Northgate Hall',173000,940,'bookshop','Pat','community programs')],
}


def opposite_stores(key, area):
    from mall.store import Store
    result=[]
    for i,(name,cost,rent,kind,*_) in enumerate(OPPOSITE[key]):
        store=Store((area.left+224+i*300,area.bottom-280,280,240),name,False,cost,rent,kind,facing='up')
        store.section_key=key;result.append(store)
    return result
