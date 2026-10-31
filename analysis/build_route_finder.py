"""Build vietnam_trip_handoff/vietnam_route_finder.html from the template, data and content files."""
import os
H = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(H, 'route_finder_template.html')).read()
s = (s.replace('__GEO__', open(os.path.join(H, 'vn_geo.json')).read())
      .replace('__BUDGET__', open(os.path.join(H, 'budget_v3.json')).read())
      .replace('__CONTENT__', open(os.path.join(H, 'route_finder_content.js')).read()))
head_end = s.index('</style>') + len('</style>')
reset = '<style>html{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>\n'
doc = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       + s[:head_end] + '\n' + reset + '</head>\n<body>\n' + s[head_end:] + '\n</body>\n</html>\n')
out = os.path.join(H, '..', 'vietnam_trip_handoff', 'vietnam_route_finder.html')
open(out, 'w').write(doc)
print('wrote', os.path.normpath(out), len(doc))
