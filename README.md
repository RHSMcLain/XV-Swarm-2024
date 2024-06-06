![header](https://capsule-render.vercel.app/api?type=waving&text=XV:%20Swarm-2024&animation=scaleIn&color=gradient&fontColor=000000&customColorList=2&height=150&fontSize=50&fontAlignY=25)
<details>  
    <summary>Description of XV-Swarm-24</summary>

        The objective of this class was to create and program swarm drones ourselves. For the first few weeks of class we worked on building the drones using a parts kit. In order to legally fly the drone, we needed approval for multiple FAA and school district waivers, some of which had to be revised. We also created the necessary code from scratch, including the keyboard and flexstick controls, the communications from the arduino to the flight controller, the access point, and the base station.
</details>

<details> 
    <summary>Regulatory Compliance</summary>

    - FAA Multi Waiver
    - RSD Multi Waiver
    - § 107.35 – Operation of Multiple Small UAS
    - Register With FAA
    - Register RSD with ODA
    - Request Fria 

</details>

<details>
    <summary>
        <h3>Drone Building Instructions and Parts List</h3>
    </summary>
    <details>
        <summary>
            <b>Frame Construction</b>
        </summary>
        <a href="https://github.com/Kbratland/DronSbusCod/blob/main/Instructions/FrameConstruction.md">Frame Instructions</a>
    </details>
    <details>
        <summary>
            <b>Wiring!</b>
        </summary>
        <a href="https://github.com/Kbratland/DronSbusCod/blob/main/Instructions/Wiring.md">Wiring Instructions</a>
    </details>
    <details>
        <summary>
            <b>Code installation and Configuration</b>
        </summary>
            <details>
                <summary>
                       Code
                </summary>
             <a href="https://github.com/Kbratland/DronSbusCod/blob/main/Instructions/CodeInstall.md">Code Installation Instructions</a>
            </details>
            <details>
                <summary>
                    Configuration
                </summary>
                <a href="https://github.com/Kbratland/DronSbusCod/blob/main/Instructions/Configuration.md">Configuration Instructions</a>
            </details>
    </details>
    <details>
        <summary>
            <b>Parts Needed:</b>
        </summary>
        -<a href="https://www.digikey.com/en/products/detail/jst-sales-america-inc/A08SR08SR30K203A/9922207">8-Pin JST Cable </a> <br>
        -<a href="https://holybro.com/collections/autopilot-flight-controllers/products/kakute-f4-v2-4">Kakute F4 v2.4 Flight Controller</a> <br>
        -<a href="https://holybro.com/collections/motors/products/ripper-1404-3800kv-ultralight-brushless-motor?variant=41563378679997">Ripper Motor Four-pack</a> <br>
        -<a href="https://www.amazon.com/1500mAh-Graphene-Quadcopter-Helicopter-Airplane/dp/B09CTS2KY6/ref=sr_1_2_sspa?crid=FK27DSRZSRYX&keywords=XT60+8s+drone+battery&qid=1697687364&sprefix=xt60+8s+drone+battery%2Caps%2C135&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1">Ovonic Lipo Battery</a> <br>
        -<a href="https://holybro.com/collections/autopilot-peripherals/products/tekko32-f4-4in1-mini-50a-esc">Tekko-32 Motor Controller</a> <br>
        -<a href="https://holybro.com/collections/power-modules-pdbs/products/pm02-v3-12s-power-module">Battery Cable Adapter</a> <br>
        -<a href="https://holybro.com/collections/standard-gps-module/products/micro-m10-m9n-gps">Micro M10 GPS</a> <br>
        -<a href="https://betafpv.com/products/hq-3030-2-blade-propellers-1-5-shaft-16-pcs?variant=29700573528108">16x 3-Blade Propellers</a> <br>
        -<a href="https://store-usa.arduino.cc/products/arduino-nano-33-iot">Arduino Nano 33 IOT</a> <br>
        -<a href="https://store.arduino.cc/products/nodemcu-esp8266">NodeMCU ESP8266</a> <br>
        <br><p>Screw and insert types below, feel free to use different than the link provides</p>
        -<a href="https://www.amazon.com/gp/product/B07TTQXVQH/ref=ox_sc_act_title_1?smid=A19TVI3M6WFVG7&th=1">M1.6 Brass Screw Insert</a> <br>
        -<a href="https://www.amazon.com/M1-6x4mm-0-35mm-Pitch-Socket-100pcs/dp/B00XP4ZWY2/ref=sr_1_13?crid=H5KH0H4M0INP&keywords=m1.6+screws&qid=1704831251&s=hi&sprefix=m1.6+screws%2Ctools%2C123&sr=1-13">M1.6 .35mm Screw</a> <br>
        -<a href="https://www.amazon.com/initeq-M3-0-5-Threaded-Inserts-Printing/dp/B077CJV3Z9?th=1">M3 Brass Screw Insert</a> <br>
        -<a href="https://www.amazon.com/Socket-Screws-Bolts-Thread-100pcs/dp/B07CNFTK99/ref=sr_1_3?crid=35UJIKL633YXJ&dib=eyJ2IjoiMSJ9.V_gDm7ESMeIo97fLWGQNmFlomiYVCGIPnWED3Y3Rms9MFpWTToYL3cxsTUpSsaV8R714BC67_QRT3Vo5RvrRcJTYQtaIVcy5crKdhkuFxj4jzhkEdaz5k46nMluhti4cHcKDeJfvPvoZlKnusmHvHRaYAluaCqt8RDdrJ6sHAZLitWjBnjSr0pAM2s8yo8Kuzl-GrbAJhoYED8w90Vbyy2n6uXMIcMTEoskzIvMzHmTOEPhf0xayDmpOBLuzhUD0515MnIU9iwsBIeh5KqbNrG-BdkdMrp81OtmZ6_xKDgk.URAu2aWqW-k1S9PAmIsFk2jZMnAW4nDT19p-t1PMlbU&dib_tag=se&keywords=m3%2B12mm%2Bscrew&qid=1717710124&s=hi&sprefix=m3%2B12mm%2Bscre%2Ctools%2C190&sr=1-3&th=1">M3 12mm Screw</a> <br>
    </details>
</details>
