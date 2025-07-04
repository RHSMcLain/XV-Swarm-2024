![header](https://capsule-render.vercel.app/api?type=waving&text=XV:%20Swarm%202023-5&animation=scaleIn&color=gradient&fontColor=000000&customColorList=2&fontAlignY=30&height=195&fontY=30&desc=Riverdale%20High%20School%20Student-Run%20Engineering%20Class&descAlignY=48)
<!Happy now Bob?>
##
<details>  
    <summary>
        <b>Description of XV: Swarm</b>
    </summary>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The objective of this class was to create and program swarm drones ourselves. For the first few weeks of class, we worked on building &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;the drones using a parts kit put together through research. To legally fly the drone, we needed approval for multiple FAA and school &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;district waivers, some of which had to be revised. We also created the code from scratch, including the keyboard and flight stick &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;controls, the communications from the Arduino to the flight controller, the access point, and the base station.</p>
</details>

<details>
    <summary> <b>Setup for programming<br></b> </summary>
        <setup>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;What you need to install:
        <details>
                <summary>Python Libraries</summary>
                <p>
                            pip3 install "requests>=2.*" <br>
                            pip3 install netifaces <i>(make sure you have C++ build tools and the SDK for your version if you are on windows)</i> <br>
                            python3 -m pip install customtkinter <br>
                            python3 -m pip install --upgrade Pillow <br>
                            pip3 install pynput <br>
                </p>
            </details>
        </setup>
</details>

<details> 
    <summary>
        <b>Regulatory Compliance</b>
    </summary>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;What we have applied for and received:<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- FAA Multi-Use Waiver<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- RSD Multi-Use Waiver<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- § 107.35 – Operation of Multiple Small UAS<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Registered each drone With FAA<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Registered RSD with ODA<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- FRIA zone <br>

</details>

<details> 
    <summary>
        <b>Summary of Flightstick Code</b>
    </summary>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Code for flight stick that outputs value for  pitch, roll, yaw, and throttle for the drone. </p>

</details>

<details> 
    <summary>
        <b>Summary of Base Station Code</b>
    </summary>
    <p><span style=width: 40px; display: inline-block;></span><span>Code for the base station and keyboard controls for pitch, roll, yaw, and throttle. The base station is responsible for transmitting and receiving signals to and from the drone's coverage area.</span></p>

</details>

<details> 
    <summary>
        <b>Summary of Access Point Code</b>
    </summary>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The access point provides WIFI, collects based station IP, and shares the base station IP with the drone. This code makes all of these possible. </p>

</details>

<details>
    <summary>
        <h3>Drone Building Instructions and Parts List</h3>
    </summary>
    <details>
        <summary>
            <b>Frame Construction</b>
        </summary>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/RHSMcLain/XV-Swarm-2024/blob/main/Instructions/FrameConstruction.md">Frame Instructions</a>
    </details>
    <details>
        <summary>
            <b>Wiring!</b>
        </summary>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/RHSMcLain/XV-Swarm-2024/blob/main/Instructions/Wiring.md">Wiring Instructions</a>
    </details>
    <details>
        <summary>
            <b>Code installation and Configuration</b>
        </summary>
            <details>
                <summary>
                       Code
                </summary>
             &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/RHSMcLain/XV-Swarm-2024/blob/main/Instructions/CodeInstall.md">Code Installation Instructions</a>
            </details>
            <details>
                <summary>
                    Configuration
                </summary>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://github.com/RHSMcLain/XV-Swarm-2024/blob/main/Instructions/Configuration.md">Configuration Instructions</a>
            </details>
    </details>
    <details>
        <summary>
            <b>Parts Needed:</b>
        </summary>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.digikey.com/en/products/detail/jst-sales-america-inc/A08SR08SR30K203A/9922207">8-Pin JST Cable </a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://holybro.com/collections/autopilot-flight-controllers/products/kakute-f4-v2-4">Kakute F4 v2.4 Flight Controller</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://holybro.com/collections/motors/products/ripper-1404-3800kv-ultralight-brushless-motor?variant=41563378679997">Ripper Motor Four-pack</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.amazon.com/1500mAh-Graphene-Quadcopter-Helicopter-Airplane/dp/B09CTS2KY6/ref=sr_1_2_sspa?crid=FK27DSRZSRYX&keywords=XT60+8s+drone+battery&qid=1697687364&sprefix=xt60+8s+drone+battery%2Caps%2C135&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1">Ovonic Lipo Battery</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://holybro.com/collections/autopilot-peripherals/products/tekko32-f4-4in1-mini-50a-esc">Tekko-32 Motor Controller</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://holybro.com/collections/power-modules-pdbs/products/pm02-v3-12s-power-module">Battery Cable Adapter</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://holybro.com/collections/standard-gps-module/products/micro-m10-m9n-gps">Micro M10 GPS</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://betafpv.com/products/hq-3030-2-blade-propellers-1-5-shaft-16-pcs?variant=29700573528108">16x 3-Blade Propellers</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://store-usa.arduino.cc/products/arduino-nano-33-iot">Arduino Nano 33 IOT</a> <br>
       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -<a href="https://store.arduino.cc/products/nodemcu-esp8266">NodeMCU ESP8266</a> <br>
        <br><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Screw and insert types below, feel free to use different than the link provides</p>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.amazon.com/gp/product/B07TTQXVQH/ref=ox_sc_act_title_1?smid=A19TVI3M6WFVG7&th=1">M1.6 Brass Screw Insert</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.amazon.com/M1-6x4mm-0-35mm-Pitch-Socket-100pcs/dp/B00XP4ZWY2/ref=sr_1_13?crid=H5KH0H4M0INP&keywords=m1.6+screws&qid=1704831251&s=hi&sprefix=m1.6+screws%2Ctools%2C123&sr=1-13">M1.6 .35mm Screw</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.amazon.com/initeq-M3-0-5-Threaded-Inserts-Printing/dp/B077CJV3Z9?th=1">M3 Brass Screw Insert</a> <br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-<a href="https://www.amazon.com/Socket-Screws-Bolts-Thread-100pcs/dp/B07CNFTK99/ref=sr_1_3?crid=35UJIKL633YXJ&dib=eyJ2IjoiMSJ9.V_gDm7ESMeIo97fLWGQNmFlomiYVCGIPnWED3Y3Rms9MFpWTToYL3cxsTUpSsaV8R714BC67_QRT3Vo5RvrRcJTYQtaIVcy5crKdhkuFxj4jzhkEdaz5k46nMluhti4cHcKDeJfvPvoZlKnusmHvHRaYAluaCqt8RDdrJ6sHAZLitWjBnjSr0pAM2s8yo8Kuzl-GrbAJhoYED8w90Vbyy2n6uXMIcMTEoskzIvMzHmTOEPhf0xayDmpOBLuzhUD0515MnIU9iwsBIeh5KqbNrG-BdkdMrp81OtmZ6_xKDgk.URAu2aWqW-k1S9PAmIsFk2jZMnAW4nDT19p-t1PMlbU&dib_tag=se&keywords=m3%2B12mm%2Bscrew&qid=1717710124&s=hi&sprefix=m3%2B12mm%2Bscre%2Ctools%2C190&sr=1-3&th=1">M3 12mm Screw</a> <br>
        <br><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Needed: 8pcs M3 x 12mm 0.5mm Pitch & 4pcs M1.6 x 4mm 0.35mm Pitch</p>
    </details>
</details>

## Contributors: 
Adam McLain,
Willem Abbassi, 
<a href="https://github.com/Kbratland" 
style="text-decoration: none">Konner Bratland</a>, 
Dylan Bratt, Nadir Chaer, Sylas Christopher, Thomas Fredricks, Lane Gilliam, Ethan Green, Xilena Hardy, Christian Hanson, <a href="https://github.com/Agupag" 
style="text-decoration: none">Connor Madriago</a>,<a href="https://github.com/assafnachum" 
style="text-decoration: none">Assaf Nachum</a>, Leo Novack, Spencer Parsons, <a href="https://github.com/drobinson-2915" 
style="text-decoration: none">David Robinson</a>,
<a href="https://github.com/bjornwroberts" 
style="text-decoration: none">Bjorn Roberts</a>, 
Max Symmes, Brendan Vasanth, <a href="https://github.com/KoderMx1" 
style="text-decoration: none">Cody Webb</a>, and Cyrus Weeden
##
<p align="center">
  <img src="https://github.com/Kbratland/XVBlendFiles/blob/main/800978_final.gif" alt="animated" />
</p>
