# SHADOW
magick convert -size 600x600 xc:none \
    -fill black -draw "roundrectangle 50,50 550,550 10,10" \
    \( +clone -background black -shadow 70x20+0+0 \) +swap \
    -background none -layers merge \
    assets/images/shadow.png

# TRIANGLE
magick -size 300x300 canvas:none \
  \( +clone \
     -fill '#d1551dff' -stroke '#a43008ff' -strokewidth 8 \
     -draw "path 'M 150,250 Q 155,240 200,100 Q 150,120 100,100 Q 145,240 150,250 Z'" \
     -blur 0x3 \
     -shadow 70x20+0+0 \
  \) \
  -compose over -composite \
  \( -fill '#d1551dff' -stroke '#a43008ff' -strokewidth 8 \
     -draw "path 'M 150,250 Q 155,240 200,100 Q 150,120 100,100 Q 145,240 150,250 Z'" \
  \) \
  -composite assets/images/triangle.png