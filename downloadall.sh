I=0
while [ $I -lt 2000 ] ; do
    wget http://www.basket.co.il/misc/Stats-XML/isr-$I.xml > /dev/null 2>&1
    let I=I+1 
done

grep -lrIZ javascript . | xargs -0 rm -f