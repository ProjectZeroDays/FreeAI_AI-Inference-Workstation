    def inject_into_page(self, page):
        """Inject fingerprint overrides into page JS context."""
        fp = self._data
        ua = fp['user_agent'].replace("'", "\\'")
        platform = fp['platform']
        hc = fp['hardware_concurrency']
        dm = fp['device_memory']
        lang = fp['language']
        langs = json.dumps(fp['languages'])
        tz = fp['timezone']
        tzoff = fp['timezone_offset']
        sw = fp['screen']['width']
        sh = fp['screen']['height']
        saw = fp['screen']['avail_width']
        sah = fp['screen']['avail_height']
        pr = fp['pixel_ratio']
        cd = fp['color_depth']
        np_count = len(fp['navigator_plugins'])
        nm_count = len(fp['navigator_mime_types'])
        script = (
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            "Object.defineProperty(navigator,'platform',{get:()=>'" + platform + "'});"
            "Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>" + str(hc) + "});"
            "Object.defineProperty(navigator,'deviceMemory',{get:()=>" + str(dm) + "});"
            "Object.defineProperty(navigator,'language',{get:()=>'" + lang + "'});"
            "Object.defineProperty(navigator,'languages',{get:()=>" + langs + "});"
            "Object.defineProperty(navigator,'userAgent',{get:()=>'" + ua + "'});"
            "Object.defineProperty(navigator,'plugins',{value:{length:" + str(np_count) + "}});"
            "Object.defineProperty(navigator,'mimeTypes',{value:{length:" + str(nm_count) + "}});"
            "Object.defineProperty(navigator,'connection',{get:()=>({rtt:50,effectiveType:'4g',downlink:10})});"
            "Object.defineProperty(navigator,'bluetooth',{get:()=>undefined});"
            "Object.defineProperty(navigator,'usb',{get:()=>undefined});"
            "Object.defineProperty(navigator,'hid',{get:()=>undefined});"
            "Object.defineProperty(navigator,'serial',{get:()=>undefined});"
            "Object.defineProperty(screen,'width',{get:()=>" + str(sw) + "});"
            "Object.defineProperty(screen,'height',{get:()=>" + str(sh) + "});"
            "Object.defineProperty(screen,'availWidth',{get:()=>" + str(saw) + "});"
            "Object.defineProperty(screen,'availHeight',{get:()=>" + str(sah) + "});"
            "Object.defineProperty(window,'devicePixelRatio',{get:()=>" + str(pr) + "});"
            "Object.defineProperty(window,'orientation',{get:()=>({type:'landscape-primary',angle:0})});"
            "Object.defineProperty(window,'colorDepth',{get:()=>" + str(cd) + "});"
            "Object.defineProperty(Date,'getTimezoneOffset',{value:()=> " + str(tzoff) + "});"
            "Object.defineProperty(Intl.DateTimeFormat.prototype,'formatToParts',{value:function(){return [];}});"
            "const origRTCP=RTCPeerConnection;"
            "window.RTCPeerConnection=function(...args){"
            "  const pc=new origRTCP(...args);"
            "  const origGetStats=pc.getStats.bind(pc);"
            "  pc.getStats=function(...a){return origGetStats().then(r=>{"
            "    for(const x of r.values()){if(x.type==='candidate'&&x.candidate)x.candidate=x.candidate.replace(/([0-9]+\\\\.){3}[0-9]+/g,'0.0.0.0');}"
            "    return r;});};"
            "  return pc;};"
            "const origOpenDB=indexedDB.open;"
            "indexedDB.open=function(){return origOpenDB.apply(this,arguments);};"
            "const origPerf=performance.now;"
            "performance.now=function(){return origPerf.call(performance);;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;"
            "const origEnum=navigator.enumerateDevices;"
            "if(origEnum){navigator.enumerateDevices=function(){return Promise.resolve([]);}};"
        )
        page.add_init_script(script)
