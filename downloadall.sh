I=1906
let I=I+1 
while [ $I -lt 2100 ] ; do
    if [ ! -f isr-$I.xml ]; then
        echo "http://www.basket.co.il/misc/Stats-XML/isr-$I.xml?"
        exit
        wget http://www.basket.co.il/misc/Stats-XML/isr-$I.xml? > /dev/null 2>&1
        echo "isr-$I.xml downloaded"
    fi
    let I=I+1 
done

grep -lrIZ javascript . | xargs -0 rm -f

