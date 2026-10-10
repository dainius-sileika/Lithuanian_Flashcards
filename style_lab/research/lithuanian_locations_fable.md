# Lithuanian location bank — real places for the GO deck (free Lithuania, 1981)
Research note, 2026-10-11. Companion file: `location_bank.json` (same content, machine-readable). Fiction frame: late-Soviet visual culture, free Lithuania, tricolour only, no Soviet symbols. Cards are small, so each place is reduced to 1–3 drawable features; the prompt phrase describes the look, because image models ignore or garble place names.

## 0. Method and sources
- Primary source for almost every entry: Visuotinė lietuvių enciklopedija (VLE) articles, read via their text (URLs per entry). Supplementary: UNESCO WHL/ICH pages, English Wikipedia for the TV tower, Vilnius trolleybuses, Šiauliai and Panevėžys.
- `state_1981` lines give what the sources date; anything I could not date from a read source is listed under *unverified*. Later additions (statues, churches, piers built after 1981) are listed so they can be excluded.
- Counterfactual adjustments are deductions from the sources' Soviet-era facts (e.g. VLE records that the Soviets removed the cathedral statues in 1950 and turned the Resurrection church into a radio factory); in a free 1981 those events did not happen.

## 1. Universal counterfactual rules (apply to every located card)
- Universal counterfactual rules: tricolour only; no Lenin/Soviet emblems, slogans, red stars; Catholic churches in use; Vilnius Cathedral has its three pediment statues; Kaunas Resurrection church is complete; Hill of Crosses undisturbed; Kaunas Vytautas monument standing; Palanga 'Blessing Christ' standing.
- Trolleybuses: Vilnius system opened 1956, Škoda 8Tr/9Tr in the 1960s–70s, 14Tr from 1984 (https://en.wikipedia.org/wiki/Trolleybuses_in_Vilnius). Czechoslovak Škodas are plausible imports for a free Lithuania; draw a boxy two-door trolleybus with twin poles, no slogans. Kaunas trolleybus (1965) **unverified** — page not reachable.
- Railway: Kaunas station 1953 (VLE architecture article); Vilnius station building 1950 **unverified**. Narrow-gauge line at Panevėžys (viaduct 1938).
- Housing: Lazdynai-type panel districts are kept (they read as 1970s modernism), without roof slogans.

## 2. Location entries
Columns: signature features · how it looked in 1981 · exclude (later/demolished) · counterfactual change · kitsch risk · recognisability · prompt phrase (≤30 words) · naming helps? · sources.

### Vilnius Old Town street  (`vilnius_old_town`, Vilnius, city street)
- Features: narrow curving cobbled lane between 3-storey rendered houses in ochre, pink and pale green; baroque church tower or gable closing the view; arched gateway into a courtyard
- 1981: Existed as now; facades shabbier, fewer shop signs, cobbles and trolleybus wires on the wider streets.
- Exclude: Gediminas monument on Cathedral Square (1996); Užupis angel (2001)
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (22 words): *narrow curving cobbled lane, tall rendered houses in ochre and faded pink, a baroque church tower closing the view, arched courtyard gate*
- Card categories: street, city, shop, transport, church, school
- Sources: https://www.vle.lt/straipsnis/vilniaus-katedra-ir-varpine/ ; https://www.vle.lt/straipsnis/uzupis/

### Gediminas Hill and tower  (`vilnius_gediminas_hill`, Vilnius, landmark)
- Features: octagonal red-brick tower stump on a steep wooded hill; tricolour on the tower; river Neris or cathedral roofs below
- 1981: Western tower stands (conserved 1930–39; upper floor rebuilt); museum inside since 1960. Funicular up the hill is later.
- Exclude: funicular to the hill (2003, unverified date)
- Counterfactual: Tricolour on the tower is historically correct for 1919/1939 and the natural choice for the counterfactual; no Soviet flag.
- Kitsch risk: medium; recognisability at card scale: high; naming the place helps: yes
- Prompt (19 words): *steep green hill above red roofs, squat octagonal red-brick tower on top flying a yellow-green-red flag, river bend below*
- Card categories: city, nature, weather, leisure
- Sources: https://www.vle.lt/straipsnis/aukstutine-pilis/

### Vilnius Cathedral and belfry  (`vilnius_cathedral`, Vilnius, landmark)
- Features: white classical temple front with six Doric columns and three statues on the pediment; free-standing round-based belfry with a helm roof beside it; wide empty square
- 1981: Under Soviet rule it was a picture gallery (taken 1953, returned 1988) and the three pediment statues were removed in 1950 (restored 1997). Roof re-coppered and facades repainted 1980; interior restored from 1981.
- Exclude: Gediminas monument (1996)
- Counterfactual: Draw it as a working cathedral WITH the three pediment statues (Helena, Casimir, Stanislaus) — the Soviet removal never happened. Belfry lower part housed a Soviet excursion bureau 1965–89; in the counterfactual just a belfry.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: yes
- Prompt (24 words): *white colonnaded cathedral front with three statues on the pediment, a tall free-standing round bell tower with a dark helm roof, wide paved square*
- Card categories: church, city, square, holiday
- Sources: https://www.vle.lt/straipsnis/vilniaus-katedra-ir-varpine/

### Gate of Dawn (Aušros vartai)  (`vilnius_gate_of_dawn`, Vilnius, landmark)
- Features: street closed by a three-storey gate with a renaissance attic; chapel windows above the arch; pilgrims and candles
- 1981: As now; the attic relief carries the Grand Duchy coat of arms (griffins) — heraldry, keep it as a blur.
- Counterfactual: Open religious practice is normal in the counterfactual; crowds at the chapel are correct.
- Kitsch risk: medium; recognisability at card scale: medium; naming the place helps: no
- Prompt (22 words): *narrow street ending in a tall old city gate, chapel windows over the arch, people kneeling on cobbles below, baroque church beside*
- Card categories: church, street, holiday, family
- **Unverified:** The relief shows a coat of arms — draw as indistinct carving.
- Sources: https://www.vle.lt/straipsnis/ausros-vartai/

### Užupis over the Vilnia  (`vilnius_uzupis`, Vilnius, district)
- Features: small river with a stone bridge; crooked old houses stacked up a slope; Bernardine church towers across the water
- 1981: Run-down artisan quarter in 1981; no Angel (2001), no republic signs.
- Exclude: Užupis angel (2001); art incubator and installations (2002+)
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (20 words): *small fast river under a stone bridge, crooked old houses climbing a slope, church towers across the water, washing lines*
- Card categories: river, street, home, work
- Sources: https://www.vle.lt/straipsnis/uzupis/

### Antakalnis — Sts Peter and Paul  (`vilnius_antakalnis`, Vilnius, district)
- Features: twin-towered white baroque church on a rise; wooded hills and pine; hospital complex 1954/1973
- 1981: Church open throughout (it held St Casimir's relics 1953–89). Hospital blocks 1954 and 1973; polyclinics 1983–84 are borderline.
- Exclude: adult polyclinic (1983); children's polyclinic (1984)
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (23 words): *white baroque church with two towers and a dome on a wooded rise, pine trees, a long hospital block of the 1970s nearby*
- Card categories: hospital, church, city, nature
- Sources: https://www.vle.lt/straipsnis/antakalnis/

### Neris embankment  (`vilnius_neris_embankment`, Vilnius, riverside)
- Features: wide slow river with grassy banks and a concrete-railed embankment; bridges; church towers one side, new blocks the other
- 1981: Žaliasis tiltas (1948–52) and later bridges exist; Soviet statues on the Green Bridge are OUT for the counterfactual.
- Counterfactual: Green Bridge without its 1952 Socialist-realist statue groups.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (24 words): *wide slow river with grassy banks, low concrete embankment railing, a bridge, church towers on one bank and pale new blocks on the other*
- Card categories: river, water, weather, leisure, transport
- **Unverified:** Green Bridge statue date 1952 is from the VLE architecture article (bridge 1948–52); statues' exact date unverified.
- Sources: https://www.vle.lt/straipsnis/lietuvos-architektura-1945-1990/

### Žvėrynas wooden houses  (`vilnius_zverynas`, Vilnius, district)
- Features: two-storey wooden villas with fretwork eaves and glazed verandas; lime and maple street trees; small Orthodox church dome
- 1981: Intact wooden suburb; many houses shabby, some divided into flats.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (19 words): *quiet street of two-storey wooden villas, fretwork eaves, glazed verandas, tall limes, a small onion dome at the end*
- Card categories: home, street, family, school, seasons
- Sources: https://www.vle.lt/straipsnis/zverynas/

### Vingis Park  (`vilnius_vingis`, Vilnius, park)
- Features: tall pines on river terraces; the 1960 song-festival stage shell; river bend
- 1981: Stage 1960 (Kotli/Alekna); song festivals held here; stadium 1954.
- Counterfactual: Song festival crowds in folk costume are correct; replace Soviet banners with the tricolour.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (18 words): *tall pines on a river terrace, a great concrete band-shell stage facing a sloping field, river bend behind*
- Card categories: leisure, music, nature, sport, summer
- Sources: https://www.vle.lt/straipsnis/vingio-parkas/

### Kalvarijų market  (`vilnius_kalvariju_market`, Vilnius, market)
- Features: open stalls under a long low roof; women in headscarves selling from baskets; wooden crates and scales
- 1981: Historic market on the right bank; details of its 1981 buildings not verified.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (21 words): *open market stalls under a long low roof, women in headscarves behind baskets of apples and curd, brass scales, wooden crates*
- Card categories: market, shop, food, money, work
- **Unverified:** Kalvarijų market history not verified in a read source; treat as a generic Vilnius market.
- Sources: none read (generic)

### Vilnius TV tower (1980)  (`vilnius_tv_tower`, Vilnius, landmark)
- Features: very tall thin concrete shaft with one saucer disc two-thirds up; pine tops and panel blocks below
- 1981: Finished 1980 (326.5 m, deck at 165 m) in Karoliniškės; brand new in 1981.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (22 words): *very tall thin concrete tower with a single saucer-shaped disc near the top, pine tops and nine-storey panel blocks at its foot*
- Card categories: city, technology, television, far, high
- Sources: https://en.wikipedia.org/wiki/Vilnius_TV_Tower

### Lazdynai housing district  (`vilnius_lazdynai`, Vilnius, district)
- Features: 5- and 9-storey pale panel blocks stepped on a pine slope; pedestrian paths, sculptures; footbridge over the ring road
- 1981: Begun 1967, finished 1974 (Lenin Prize 1974). Litexpo 1980. Pure late-Soviet modernism — in the counterfactual it reads as 1970s Nordic-style housing; no slogans on roofs.
- Exclude: sculpture Darbininkas 1983; Kanklininkė 1982
- Counterfactual: Keep the architecture, drop roof slogans and red banners.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (18 words): *pale prefabricated apartment blocks stepped along a pine-wooded slope, footpaths between, a Žiguli-sized car on a wide road*
- Card categories: home, city, school, family, transport
- Sources: https://www.vle.lt/straipsnis/lazdynai/ ; https://www.vle.lt/straipsnis/lietuvos-architektura-1945-1990/

### Kaunas — Laisvės alėja  (`kaunas_laisves_aleja`, Kaunas, city street)
- Features: long straight boulevard with two rows of limes; two-storey eclectic facades; 1980 fountain; Vytautas monument
- 1981: Fountain 1980; pedestrianised boulevard character; Vytautas the Great monument (1932) was destroyed 1952 and rebuilt 1990.
- Exclude: Dolskis statue (2007)
- Counterfactual: Vytautas monument (1932) still standing in the counterfactual.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (18 words): *long straight boulevard with a double row of clipped limes, two-storey ornate facades, a round fountain, people strolling*
- Card categories: street, city, shop, cafe, leisure, transport
- Sources: https://www.vle.lt/straipsnis/laisves-aleja/

### Kaunas interwar modernism  (`kaunas_modernism`, Kaunas, city street)
- Features: pale smooth rendered 4–6 storey facades, rounded corners, ribbon windows, flat roofs; Christ's Resurrection church tower on the hill
- 1981: ~1,500 interwar buildings (UNESCO 2023). All present in 1981.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (17 words): *pale smooth rendered modernist building with rounded corner and horizontal window bands, flat roof, 1930s lettering-free facade*
- Card categories: city, office, bank, post, school, work
- **Unverified:** Visual traits (rounded corners, ribbon windows) are my generalisation; UNESCO page gives few visual details.
- Sources: https://whc.unesco.org/en/list/1661/

### Christ's Resurrection church, Žaliakalnis  (`kaunas_resurrection_church`, Kaunas, landmark)
- Features: white stepped block with a 70 m square tower of narrow vertical slits; smaller stepped tower over the altar; seen above the city from the river
- 1981: Built 1934–40, unfinished; Soviets turned it into the Banga radio factory (returned 1988, completed 2004).
- Counterfactual: Draw it COMPLETED and white as a church — the key counterfactual marker of Kaunas.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: yes
- Prompt (22 words): *white monumental church, tall square tower pierced by narrow vertical slit windows, stepped smaller tower behind, on a hill above red roofs*
- Card categories: church, city, high, holiday
- Sources: https://www.vle.lt/straipsnis/kristaus-prisikelimo-bazilika/

### Kaunas Old Town and the confluence  (`kaunas_old_town_confluence`, Kaunas, landmark)
- Features: red-brick Gothic (Perkūnas house, castle round tower); white town hall 'swan' spire; two rivers meeting at a grassy point
- 1981: As now; Santaka park largely as grass.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (19 words): *red-brick Gothic castle tower and church gables, slender white town-hall spire, two wide rivers meeting at a grassy point*
- Card categories: river, city, church, square, water
- **Unverified:** Perkūnas house / town-hall details not re-verified in this pass.
- Sources: https://www.vle.lt/straipsnis/kaunas/

### Žaliakalnis funicular  (`kaunas_funicular`, Kaunas, transport)
- Features: small boxy wooden-sided car on a steep straight track; stairs beside, trees; view over the city roofs
- 1981: Two funiculars (Žaliakalnis 1931, Aleksotas 1935 — VLE gives 'two funiculars'; years unverified).
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (19 words): *small boxy funicular car on a steep straight rail track between trees, wooden station hut below, city roofs beyond*
- Card categories: transport, up, down, city
- **Unverified:** Opening years 1931/1935 unverified here.
- Sources: https://www.vle.lt/straipsnis/kaunas/ ; https://www.vle.lt/straipsnis/keltuvas/

### Pažaislis monastery  (`kaunas_pazaislis`, Kaunas, landmark)
- Features: baroque church with a tall hexagonal dome and two towers; long monastery wall; pine woods and the Kaunas lagoon
- 1981: Kaunas lagoon (1959) exists. Monastery used as a psychiatric hospital/ museum under the Soviets.
- Counterfactual: Working convent (Sisters of St Casimir since 1920) in the counterfactual.
- Kitsch risk: medium; recognisability at card scale: medium; naming the place helps: no
- Prompt (20 words): *pink-and-white baroque monastery church with a tall domed drum and twin towers behind a long wall, pines, a wide reservoir*
- Card categories: church, water, leisure, nature
- **Unverified:** Dome colour/shape detail from general knowledge.
- Sources: https://www.vle.lt/straipsnis/pazaislis/

### Kaunas railway station (1953)  (`kaunas_railway_station`, Kaunas, transport)
- Features: symmetrical stone-faced station with a clock tower; green electric train; wide forecourt
- 1981: Built 1953 (architect P. Ašastinas), Stalinist-neoclassical.
- Counterfactual: In a free Lithuania the style would differ; acceptable as 'heavy 1950s neoclassical station' without emblems.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (20 words): *symmetrical stone-faced railway station with a central clock tower, green carriages at a low platform, wide forecourt with a bus*
- Card categories: transport, train, travel, station
- Sources: https://www.vle.lt/straipsnis/lietuvos-architektura-1945-1990/

### Klaipėda old town  (`klaipeda_old_town`, Klaipėda, city street)
- Features: timber-framed (fachwerk) warehouses with dark beams on white; steep red tiled roofs; cobbled quay on the Danė
- 1981: Fachwerk and brick warehouses (18th–19th c.) on Aukštoji/Daržų streets survive; theatre square. Ännchen statue absent until 1989.
- Exclude: Ännchen von Tharau statue (restored 1989); sailing ship Meridianas on the Danė (placed 1971, unverified)
- Counterfactual: Queen of Peace church (1960) was converted to a concert hall in 1963 — in the counterfactual it stands as a church with its tall tower.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: yes
- Prompt (19 words): *timber-framed warehouses, dark beams on whitewashed infill, steep red-tiled roofs, cobbled quay along a small river with moored boats*
- Card categories: port, street, city, work, ship, river
- Sources: https://www.vle.lt/straipsnis/klaipedos-architektura/ ; https://www.vle.lt/straipsnis/klaipedos-istorija/

### Klaipėda port and Smiltynė ferry  (`klaipeda_port_ferry`, Klaipėda, port)
- Features: cranes and black-hulled ships across the strait; small flat ferry crossing to a pine-and-dune shore; red-and-white lighthouse
- 1981: Ferry to Smiltynė operates; Sea Museum in Kopgalis fort opened 1979.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (22 words): *harbour cranes and a dark ship's hull across a narrow strait, a small flat passenger ferry crossing to a pine-covered sandy shore*
- Card categories: transport, ship, sea, work, travel
- **Unverified:** Ferry service history not verified in a read source.
- Sources: https://www.vle.lt/straipsnis/klaipedos-architektura/

### Šiauliai — cathedral and Vilniaus street  (`siauliai`, Šiauliai, city)
- Features: tall white renaissance cathedral with a single very tall spire; long straight pedestrian street with lamps and benches
- 1981: Cathedral (1625) stands; Vilniaus street boulevard pedestrianised in the 1970s (year unverified). Sundial square with golden archer is 1986 — OUT.
- Exclude: Sundial square and 'Šaulys' golden archer (1986, unverified)
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (22 words): *tall white church with one very tall pointed spire above a long straight pedestrian street, lamp posts, benches, low 1970s shop fronts*
- Card categories: city, street, shop, bicycle
- **Unverified:** Pedestrian street date (1975) and sundial (1986) unverified.
- Sources: https://en.wikipedia.org/wiki/%C5%A0iauliai ; https://www.vle.lt/straipsnis/siauliai-1/

### Panevėžys — Nevėžis and theatre  (`panevezys`, Panevėžys, city)
- Features: low flat town on a slow river with an old riverbed pond (Senvagė); 1967 modernist drama theatre; narrow-gauge railway
- 1981: Theatre building 1967; cathedral 1930; narrow-gauge viaduct 1938; Ekranas factory 1962.
- Kitsch risk: low; recognisability at card scale: low; naming the place helps: no
- Prompt (20 words): *flat quiet town, slow river with a willow-lined old-riverbed pond, a low 1960s modernist theatre block, a tiny narrow-gauge train*
- Card categories: city, theatre, river, train, factory
- Sources: https://en.wikipedia.org/wiki/Panev%C4%97%C5%BEys ; https://www.vle.lt/straipsnis/panevezys/ ; https://www.vle.lt/straipsnis/ekranas-1/

### Trakai island castle  (`trakai_castle`, Trakai, landmark)
- Features: red-brick castle with a tall square keep on a small island; wooden footbridge over the lake; rowing boats and reeds
- 1981: Palace rebuilt 1953–62 (museum); forecastle completed 1987.
- Exclude: forecastle restoration (1987) — draw the outer ward lower/partly ruined
- Kitsch risk: medium; recognisability at card scale: high; naming the place helps: yes
- Prompt (18 words): *red-brick castle with a tall square keep on a small lake island, long wooden footbridge, rowing boats, reeds*
- Card categories: lake, water, leisure, boat, history, summer
- Sources: https://www.vle.lt/straipsnis/traku-pilys/

### Trakai Karaim street  (`trakai_karaim_street`, Trakai, village street)
- Features: small wooden houses gable-end to the street, each with three windows in the gable; painted shutters; lake behind
- 1981: Karaim houses as now; kenesa stands.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: yes
- Prompt (21 words): *row of small wooden houses set gable-end to the street, each gable with exactly three windows, painted shutters, lake glimpsed behind*
- Card categories: home, street, village, food
- Sources: https://www.vle.lt/straipsnis/lietuvos-karaimai/

### Druskininkai spa  (`druskininkai`, Druskininkai, resort)
- Features: pine forest on a steep Nemunas bank; wooden spa villas with verandas; colonnaded 1980 balneology building
- 1981: Balneology building 1980 (Šilinskai); interwar villas; Soviet sanatoria blocks of the 1970s exist.
- Counterfactual: Sanatoria without Soviet names; interwar-villa character foregrounded.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (22 words): *pine forest on a steep river bank, wooden spa villas with glazed verandas, a low white colonnaded spa building, people with cups*
- Card categories: hospital, health, leisure, forest, river
- Sources: https://www.vle.lt/straipsnis/druskininkai/ ; https://www.vle.lt/straipsnis/lietuvos-architektura-1945-1990/

### Palanga pier and Birutė hill  (`palanga`, Palanga, resort)
- Features: long wooden pier into the sea; wooded dune with a small brick chapel on top; pine-lined Basanavičius street
- 1981: Pier wooden (1882/1932) until the 1998 concrete one; Birutė chapel 1869; Tiškevičiai palace = Amber Museum since 1963; Jūratė ir Kastytis 1961, Birutė statue 1965, Šaulys 1981.
- Exclude: concrete pier (1998)
- Counterfactual: 'Blessing Christ' statue in the palace park (1901) was removed 1952 — present in the counterfactual.
- Kitsch risk: medium; recognisability at card scale: high; naming the place helps: yes
- Prompt (22 words): *long wooden pier on piles running out into a grey sea, wooded dune with a small brick chapel on top, pines, bathers*
- Card categories: sea, beach, summer, leisure, weather, holiday
- Sources: https://www.vle.lt/straipsnis/palanga/ ; https://www.vle.lt/straipsnis/palangos-istorija/ ; https://www.vle.lt/straipsnis/palangos-architektura/ ; https://www.vle.lt/straipsnis/birutes-kalnas/

### Nida and the Curonian Spit  (`nida_curonian_spit`, Neringa, landscape)
- Features: huge bare sand dune falling to a lagoon; low fishermen's houses with reed roofs and carved weathervanes; flat-bottomed boat
- 1981: Lutheran church 1888, Thomas Mann house 1930, lighthouse; Neringa town since 1961; Catholic church 2003 — OUT.
- Exclude: Catholic church (2003); amber gallery (1995)
- Kitsch risk: medium; recognisability at card scale: high; naming the place helps: yes
- Prompt (21 words): *huge bare sand dune sloping to a flat lagoon, low wooden fishermen's houses with reed-thatched roofs and a carved pierced weathervane*
- Card categories: sea, sand, fish, boat, wind, summer, home
- **Unverified:** House colours (blue/brown with white trim) not verified in a read source.
- Sources: https://www.vle.lt/straipsnis/nida/ ; https://www.vle.lt/straipsnis/kursiu-nerija/ ; https://www.vle.lt/straipsnis/vejarodis/

### Kernavė mounds  (`kernave`, Širvintos district, landscape)
- Features: four grassy flat-topped mounds side by side above a river valley; wooden footpaths; neo-Gothic brick church behind
- 1981: Mounds as now; church c. 1920; UNESCO 2004; Moses statue 2000 — OUT; no festival.
- Exclude: Moses statue (2000); archaeology festival (1999+)
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: yes
- Prompt (20 words): *four steep grassy flat-topped mounds in a row above a wide river valley, a small brick neo-Gothic church behind them*
- Card categories: hill, history, river, nature, walk
- Sources: https://www.vle.lt/straipsnis/kernaves-piliakalniai/ ; https://www.vle.lt/straipsnis/kernave/

### Hill of Crosses  (`hill_of_crosses`, near Šiauliai, landmark)
- Features: small mound bristling with thousands of wooden and iron crosses; flat fields around; a path up the middle
- 1981: Soviets bulldozed it 1961 and 1973–75; crosses rebuilt secretly. In the counterfactual it is dense and undisturbed.
- Counterfactual: Draw it full, old and weathered — no destruction ever happened.
- Kitsch risk: high; recognisability at card scale: high; naming the place helps: yes
- Prompt (21 words): *small grassy mound crowded with thousands of wooden and iron crosses of every size, path up the middle, flat fields around*
- Card categories: church, holiday, hill, history
- Sources: https://www.vle.lt/straipsnis/kryziu-kalnas/ ; https://ich.unesco.org/en/RL/cross-crafting-and-its-symbolism-00013

### Rumšiškės-type farmstead (open-air museum)  (`rumsiskes_farmstead`, Kaišiadorys district, farm)
- Features: log farmhouse, granary on stones, wattle fence, sweep well; orchard and roadside cross
- 1981: Museum opened 1974 (unverified date); used here as the generic authentic farmstead model.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (20 words): *log farmhouse with wide eaves, small granary on corner stones with open gallery, wattle fence, sweep well, orchard, roadside cross*
- Card categories: farm, animals, crops, home, village, work
- **Unverified:** Museum opening year unverified.
- Sources: https://www.vle.lt/straipsnis/lietuvos-etnografijos-muziejus/ ; https://www.vle.lt/straipsnis/lietuviu-tradicines-sodybos/

### Žemaitija farmstead  (`zemaitija_village`, Žemaitija, farm)
- Features: long low troba with half-hipped roof and gable vents, wide eaves; ponds and many trees; wooden koplytstulpis at the gate
- 1981: Many such farmsteads survived in Žemaitija; in the counterfactual all do.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (23 words): *long low log farmhouse with half-hipped roof, triangular gable vents and deep eaves, pond, big old trees, a roofed shrine-post at the gate*
- Card categories: farm, home, animals, rain, autumn
- Sources: https://www.vle.lt/straipsnis/troba/ ; https://www.vle.lt/straipsnis/lietuviu-tradicines-sodybos/ ; https://www.vle.lt/straipsnis/koplytstulpiai/

### Aukštaitija street village and lakes  (`aukstaitija_village`, Aukštaitija, village)
- Features: houses in a row gable-end to one street; white interiors; lake and hills behind
- 1981: Street villages mostly broken up by 1939; in a free Lithuania more single farms, but a few street villages remain (Aukštaitija NP).
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (21 words): *row of small log houses set gable-end to a single village street, picket fences, a long lake and low hills behind*
- Card categories: village, lake, home, school, neighbour
- Sources: https://www.vle.lt/straipsnis/lietuviu-tradicines-gyvenvietes/ ; https://www.vle.lt/straipsnis/labanoro-regioninis-parkas/

### Dzūkija forest village  (`dzukija_village`, Dzūkija, village)
- Features: log pirkia with projecting corner logs and painted two-colour shutters; sandy track, pine forest; mushroom baskets
- 1981: Forest villages (Marcinkonys, Zervynos type) intact.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (18 words): *small log house with projecting corner joints and two-colour painted shutters, sandy track, tall pines, baskets of mushrooms*
- Card categories: forest, village, home, mushroom, berry, autumn
- Sources: https://www.vle.lt/straipsnis/pirkia/ ; https://www.vle.lt/straipsnis/cepkeliu-raistas/

### Suvalkija single farmstead  (`suvalkija_farm`, Suvalkija, farm)
- Features: symmetrical boarded stuba with red clay-tile roof and glazed porch; square yard ringed by rows of trees; flat rich fields
- 1981: Prosperous interwar farms; the counterfactual keeps them.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (20 words): *symmetrical boarded farmhouse with red clay-tile roof and glazed porch, square yard ringed by rows of tall trees, flat fields*
- Card categories: farm, crops, home, summer, work
- Sources: https://www.vle.lt/straipsnis/stuba/ ; https://www.vle.lt/straipsnis/lietuviu-tradicines-sodybos/

### Neris valley  (`neris_valley`, Vilnius–Kernavė, landscape)
- Features: wide river in a deep wooded valley with sandy bluffs; pine on the bluffs; wooden boat
- 1981: As now.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (20 words): *wide river curving through a deep wooded valley, pale sandy bluff on the outer bank, pines above, a wooden boat*
- Card categories: river, water, nature, swim, summer
- Sources: https://www.vle.lt/straipsnis/kernaves-piliakalniai/ ; https://www.vle.lt/straipsnis/vingio-parkas/

### Nemunas valley  (`nemunas_valley`, Kaunas–Jurbarkas, landscape)
- Features: very wide river with high steep banks, castle mounds and manor spires; ferry or barge
- 1981: As now.
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (19 words): *very wide slow river with high steep wooded banks, a small flat ferry, a church spire on the bluff*
- Card categories: river, boat, travel, nature
- Sources: https://www.vle.lt/straipsnis/druskininkai/

### Aukštaitija lakes (Labanoras)  (`aukstaitija_lakes`, Aukštaitija, landscape)
- Features: chain of long lakes between wooded hills; reeds, rowing boat, fishing; wooden church bell-tower on shore
- 1981: Labanoras region: 285 lakes, Labanoras belfry.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (19 words): *long narrow lake between pine-wooded hills, reed beds, a wooden rowing boat, a small wooden bell-tower on the shore*
- Card categories: lake, fish, boat, summer, winter, nature
- Sources: https://www.vle.lt/straipsnis/labanoro-regioninis-parkas/

### Dzūkija pine forest  (`dzukija_pine_forest`, Dzūkija, landscape)
- Features: straight pine trunks on pale sand and lichen; heather; mushroom pickers
- 1981: As now.
- Kitsch risk: low; recognisability at card scale: high; naming the place helps: no
- Prompt (17 words): *straight red-brown pine trunks on pale sand and grey lichen, heather, a figure with a wicker basket*
- Card categories: forest, tree, mushroom, walk, autumn
- Sources: https://www.vle.lt/straipsnis/cepkeliu-raistas/ ; https://www.vle.lt/straipsnis/druskininkai/

### Čepkeliai raised bog  (`cepkeliai_bog`, Dzūkija, landscape)
- Features: flat open bog with sparse stunted pines; cotton grass, dark pools; distant dune ridge
- 1981: Reserve since 1975; boardwalk later.
- Exclude: educational boardwalk and tower (later, unverified)
- Kitsch risk: low; recognisability at card scale: medium; naming the place helps: no
- Prompt (19 words): *flat open bog with sparse stunted pines, white cotton-grass tufts, dark still pools, a low wooded ridge far off*
- Card categories: nature, bird, wet, spring, berry
- Sources: https://www.vle.lt/straipsnis/cepkeliu-raistas/

## 3. Card category → locations
- **street_city**: Vilnius Old Town street (`vilnius_old_town`), Kaunas — Laisvės alėja (`kaunas_laisves_aleja`), Kaunas interwar modernism (`kaunas_modernism`), Klaipėda old town (`klaipeda_old_town`), Šiauliai — cathedral and Vilniaus street (`siauliai`), Lazdynai housing district (`vilnius_lazdynai`), Žvėrynas wooden houses (`vilnius_zverynas`)
- **transport**: Žaliakalnis funicular (`kaunas_funicular`), Kaunas railway station (1953) (`kaunas_railway_station`), Klaipėda port and Smiltynė ferry (`klaipeda_port_ferry`), Vilnius Old Town street (`vilnius_old_town`), Kaunas — Laisvės alėja (`kaunas_laisves_aleja`), Lazdynai housing district (`vilnius_lazdynai`), Panevėžys — Nevėžis and theatre (`panevezys`)
- **market_shop**: Kalvarijų market (`vilnius_kalvariju_market`), Kaunas — Laisvės alėja (`kaunas_laisves_aleja`), Šiauliai — cathedral and Vilniaus street (`siauliai`), Vilnius Old Town street (`vilnius_old_town`)
- **school**: Lazdynai housing district (`vilnius_lazdynai`), Žvėrynas wooden houses (`vilnius_zverynas`), Kaunas interwar modernism (`kaunas_modernism`), Aukštaitija street village and lakes (`aukstaitija_village`)
- **hospital_health**: Antakalnis — Sts Peter and Paul (`vilnius_antakalnis`), Druskininkai spa (`druskininkai`), Kaunas interwar modernism (`kaunas_modernism`)
- **church_holiday**: Vilnius Cathedral and belfry (`vilnius_cathedral`), Gate of Dawn (Aušros vartai) (`vilnius_gate_of_dawn`), Christ's Resurrection church, Žaliakalnis (`kaunas_resurrection_church`), Hill of Crosses (`hill_of_crosses`), Antakalnis — Sts Peter and Paul (`vilnius_antakalnis`), Pažaislis monastery (`kaunas_pazaislis`), Aukštaitija lakes (Labanoras) (`aukstaitija_lakes`)
- **farm_animals_crops**: Rumšiškės-type farmstead (open-air museum) (`rumsiskes_farmstead`), Žemaitija farmstead (`zemaitija_village`), Suvalkija single farmstead (`suvalkija_farm`), Dzūkija forest village (`dzukija_village`), Aukštaitija street village and lakes (`aukstaitija_village`)
- **water_weather_seasons**: Aukštaitija lakes (Labanoras) (`aukstaitija_lakes`), Neris valley (`neris_valley`), Nemunas valley (`nemunas_valley`), Palanga pier and Birutė hill (`palanga`), Nida and the Curonian Spit (`nida_curonian_spit`), Neris embankment (`vilnius_neris_embankment`), Trakai island castle (`trakai_castle`)
- **home_interior**: Žemaitija farmstead (`zemaitija_village`), Dzūkija forest village (`dzukija_village`), Suvalkija single farmstead (`suvalkija_farm`), Trakai Karaim street (`trakai_karaim_street`), Žvėrynas wooden houses (`vilnius_zverynas`), Lazdynai housing district (`vilnius_lazdynai`), Nida and the Curonian Spit (`nida_curonian_spit`)
- **work_trades**: Klaipėda old town (`klaipeda_old_town`), Klaipėda port and Smiltynė ferry (`klaipeda_port_ferry`), Panevėžys — Nevėžis and theatre (`panevezys`), Užupis over the Vilnia (`vilnius_uzupis`), Rumšiškės-type farmstead (open-air museum) (`rumsiskes_farmstead`), Nida and the Curonian Spit (`nida_curonian_spit`)
- **leisure**: Palanga pier and Birutė hill (`palanga`), Trakai island castle (`trakai_castle`), Druskininkai spa (`druskininkai`), Vingis Park (`vilnius_vingis`), Nida and the Curonian Spit (`nida_curonian_spit`), Aukštaitija lakes (Labanoras) (`aukstaitija_lakes`)
- **nature**: Dzūkija pine forest (`dzukija_pine_forest`), Čepkeliai raised bog (`cepkeliai_bog`), Aukštaitija lakes (Labanoras) (`aukstaitija_lakes`), Neris valley (`neris_valley`), Kernavė mounds (`kernave`), Gediminas Hill and tower (`vilnius_gediminas_hill`), Nida and the Curonian Spit (`nida_curonian_spit`)

Notes per category:
- street/city words: Old Town lane (Vilnius) is the default; Laisvės alėja for 'boulevard/stroll/café'; Kaunas modernism for 'office/bank/post'; Klaipėda for 'port/sailor'; Lazdynai for 'flat/block/lift'.
- transport: trolleybus → Vilnius/Kaunas street; train → Kaunas station or Panevėžys narrow gauge; ferry/ship → Klaipėda; funicular → Kaunas; bicycle → Šiauliai (Vairas factory town) or any village.
- markets/shops: Kalvarijų market (unverified detail, so draw a generic covered market) or Laisvės alėja shopfronts.
- school: Zvėrynas wooden school street, Lazdynai school yard, interwar modernist school (Kaunas), village school (Aukštaitija).
- hospital/health: Antakalnis hospital blocks (1954/1973), Druskininkai spa.
- church: Vilnius cathedral (with statues), Gate of Dawn, Sts Peter & Paul, Resurrection church (complete), village wooden church with bell-tower, Hill of Crosses for 'cross/pray'.
- farm/animals/crops: four regional farmsteads + Rumšiškės-type generic.
- water/weather/seasons: Aukštaitija lakes (winter ice too), Neris/Nemunas, Palanga sea, Nida dune/wind, Trakai lake.
- family/home interiors: Žemaitija troba (rich colours), Dzūkija pirkia (patterned textiles), Suvalkija stuba, Karaim house, Žvėrynas villa, Lazdynai flat.
- work trades: Klaipėda docks, Panevėžys factory, Užupis workshops, farmstead crafts, Nida fishing.
- leisure: Palanga beach, Trakai boats, Druskininkai cure, Vingis song stage, Nida, lake fishing.
- nature: Dzūkija pines, Čepkeliai bog, lakes, Neris bluffs, Kernavė mounds, Gediminas hill, Curonian dunes.

## 4. Rotation rule
- Target share with a named real place: 70 % of *eligible* cards (within the owner's 2/3–3/4 band).
- Method: Deterministic: take a stable hash of the card's lemma (not its index); if hash mod 100 < 70 the card gets a location from its category list, chosen by hash mod len(list); otherwise generic. Re-roll only if the same location was used by the previous card in the same category.
- Caps: No single location above 8 % of located cards; Vilnius Old Town and Rumšiškės-type farmstead are the natural overflow sinks, so cap them first.
- Soft preference: Prefer region-generic locations (Žemaitija/Dzūkija/Suvalkija/Aukštaitija farms, Old Town street, lake, pine forest) for 2/3 of located cards and famous silhouettes (Trakai, Gediminas tower, Hill of Crosses, Nida dune, TV tower, Resurrection church) for at most 1/3, so the deck does not read as a postcard set.
- Eligible: any card whose scene has a background: places, transport, weather, seasons, work, leisure, food at table, family at home, school, church, farm, nature
- Always generic: abstract nouns and adjectives; objects shown in isolation (cup, key, pencil); body parts; numbers, colours, pronouns, function words; verbs of thinking/feeling without a scene; clothing items shown alone; animals shown alone (use farm/forest location only when the card shows a scene).

## 5. Does naming the place help the image model?
- Mostly no: diacritics and small-town names are garbled or ignored. Name only the places with a world-known silhouette (Trakai castle, Gediminas tower, Hill of Crosses, Curonian dunes, Vilnius cathedral) and even then put the description first and the name last, e.g. '…red-brick island castle with square keep (Trakai)'. For everything else use the look phrase alone.
- Never let the name pull in text: no signs, no captions, no masthead lettering on buildings.

## 6. Example staging lines
- gatvė / street — Old Town lane: narrow curving cobbled lane, ochre and pink rendered houses, baroque tower closing the view, two figures with string bags.
- traukinys / train — Kaunas station: heavy stone station with clock tower, green carriages, a man in a flat cap with a suitcase.
- laivas / ship — Klaipėda: dark ship's hull behind cranes, small flat ferry, timber-framed warehouse on the quay.
- ežeras / lake — Labanoras: long lake between pine hills, reed beds, a man in a rowing boat, wooden bell-tower on the shore.
- ūkis / farm — Suvalkija: boarded farmhouse with red tile roof and glazed porch, square yard ringed by tall trees, cart and horse.
- bažnyčia / church — Kaunas: white church with tall slit-windowed square tower on the hill, finished and in use, women in headscarves on the steps.
- paplūdimys / beach — Palanga: long wooden pier on piles into a grey sea, pines on dunes, bathers in plain dark costumes.
- kalnas / hill — Kernavė: four grassy flat-topped mounds above a wide river valley, a boy on top, brick church behind.
- butas / flat — Lazdynai: pale panel block among pines, a balcony with washing, small boxy car below.
- pelkė / bog — Čepkeliai: flat open bog, stunted pines, cotton grass, dark pools, a crane standing far off.

## 7. Consolidated unverified list
- Gate of Dawn (Aušros vartai): The relief shows a coat of arms — draw as indistinct carving.
- Neris embankment: Green Bridge statue date 1952 is from the VLE architecture article (bridge 1948–52); statues' exact date unverified.
- Kalvarijų market: Kalvarijų market history not verified in a read source; treat as a generic Vilnius market.
- Kaunas interwar modernism: Visual traits (rounded corners, ribbon windows) are my generalisation; UNESCO page gives few visual details.
- Kaunas Old Town and the confluence: Perkūnas house / town-hall details not re-verified in this pass.
- Žaliakalnis funicular: Opening years 1931/1935 unverified here.
- Pažaislis monastery: Dome colour/shape detail from general knowledge.
- Klaipėda port and Smiltynė ferry: Ferry service history not verified in a read source.
- Šiauliai — cathedral and Vilniaus street: Pedestrian street date (1975) and sundial (1986) unverified.
- Nida and the Curonian Spit: House colours (blue/brown with white trim) not verified in a read source.
- Rumšiškės-type farmstead (open-air museum): Museum opening year unverified.
- Kaunas trolleybus opening year (1965) — not reached.
- Vilnius railway station building date (1950) — not reached.
- Rumšiškės museum opening (1974) — VLE article gives no founding year in the extract read.
## 8. Bank gaps found while curating settings_assignments.csv (2026-10-11)
Cards left generic because the fitting place is not in the bank:
- **miestelis / town (039)** — a small-town market square of low wooden houses with a modest church spire (Žemaitija or Dzūkija miestelis: Kražiai, Merkinė type). Add `zemaitija_miestelis`.
- **oro uostas / airport (029) and lėktuvas / plane (012)** — Vilnius airport terminal (1954, VLE architecture article) with its heavy neoclassical front; add `vilnius_airport_1954` (draw without emblems).
- **sirgalius / fan (107)** — a stadium stand: Žalgiris stadium, Vilnius, or Kaunas Ąžuolynas sports complex (UNESCO Kaunas list names the latter). Add `kaunas_azuolynas_stadium`.
- **teismas / court (035)** — Kaunas interwar Palace of Justice on Vienybės square (unverified) would give a credible courtroom exterior; interior card, low priority.
- **plaukti / swim (370)** — a public pool; none in the bank (Lazdynai pool is later, unverified). Low priority.
- **viešbutis / hotel (032)** — assigned to Palanga, but a Vilnius option (Neringa hotel 1960, Gedimino prospektas, VLE architecture article) would be better for a city hotel; add `vilnius_gedimino_prospektas`.
- **autobusas / bus and the whole trolleybus theme** — the bank has no dedicated trolleybus-street entry; Lazdynai and the Old Town absorb it. Consider `vilnius_trolleybus_street` (Škoda 9Tr, twin poles, 1956+ system).
Unused bank entries this round (kept for future cards): vilnius_gediminas_hill, vilnius_gate_of_dawn, hill_of_crosses, kaunas_resurrection_church, kaunas_pazaislis.
