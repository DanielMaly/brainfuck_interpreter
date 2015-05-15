## Rozhraní

Rozhraní z příkazové řádky je implementováno tak, jak je uvedeno v požadavcích. Jedinou výjimkou je podpora formátu P6.
Kvůli nejednoznačnosti zadání je implementována takto: 
    
*   Funguje pouze přepínač `--pnm`. PBM jako monochromatický formát je nám k ničemu.
*   Přepínač `--pnm` lze kombinovat pouze s variantou `--f2lc`.
*   Jeho zapnutí nahradí formát PNG formátem P6 pro výstup.
*   Přepínač `--f2lc` podporuje i obrazový vstup, lze tedy překládat z PNG do P6, ovšem pouze na úrovni obsaženého
    Brainfuck kódu (ostatní informace na vstupu jsou ztraceny).
      
Parsování argumentů z příkazové řádky je uděláno pomocí modulu argparse, který je kvůli nestandardním požadavkům
trochu znásilněn. Nebylo v mých silách kontrolovat všechny možné nesmyslné kombinace parametrů, které argparsem nešlo
zakázat, takže co nedává smysl, má za následek buď Python výjimku, nebo nějakou vtipnou logickou chybu.

Help text na příkazové řádce je vygenerovaný argparsem a ke konci u parametrů `--f2lc` a `--lc2f` úplně neodpovídá 
skutečnosti (žádný variabilní počet argumentů tam není, ale nešlo specifikovat počet parametrů jako rozmezí). 
Přepínače `-o` a `--ppm` jsou kombinovatelné pouze s `--f2lc`. 


## O implementaci

Po spuštění programu se vytvoří nějaký `InputSource`, což je zdroj programových a vstupních dat pro interpreter. Pak 
se buď intepreter spustí s nějakým OutputReceiverem (prakticky se používá jenom jeden), nebo se naparsovaná vstupní data
pošlou přímo obrázkovému encoderu. Společný PNG dekodér je používán jak `InputSourcem`, tak `PNGEncoderem`. 
PNG vstup a výstup jsou dost pomalé, takže při zkoušení větších obrázků (300x225 ještě v pohodě, obrázek obsahující
hru Lost Kingdom je už horší) doporučuji mít trpělivost.

Samotný Brainfuck interpreter je třída `Binterpreter`. Snažil jsem se alespoň trochu optimalizovat rychlost běhu
ukládáním pozic otevřených závorek na zásobník. Lost Kingdom sice pořád není úplně ideálně hratelné, ale aspoň už se 
nečeká minutu na naběhnutí hry.
