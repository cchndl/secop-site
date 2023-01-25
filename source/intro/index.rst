============
Introduction
============

.. toctree::
    :maxdepth: 1

This is an interactive SECoP terminal.  You can try entering commands and see
the resulting response.

.. raw:: html

   <script src="https://cdn.jsdelivr.net/npm/xterm@4.9.0/lib/xterm.min.js"></script>
   <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.4.0/lib/xterm-addon-fit.min.js"></script>
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@4.9.0/css/xterm.min.css"></link>

   <script type="text/javascript">
   var term = null;
   var termFitAddon = null;
   var input = "";
   var counter = 0;

   function openterm() {
       $('html').addClass('is-clipped');
       term = new Terminal({'rows': 20});
       term.setOption('lineHeight', 1.2);
       termFitAddon = new FitAddon.FitAddon();
       term.loadAddon(termFitAddon);
       term.open(document.getElementById('term'));
       termFitAddon.fit();
       term.focus();
       term.write("\x1b[0;1m>\x1b[1;36m ");
       term.onData(function(data) {
           if (data == "\u007f") {
               if (input.length > 0) {
                   input = input.substr(0, input.length - 1);
                   term.write("\x08\x1b[K");
               }
           } else if (data == "\r") {
               term.write("\r\n");
               if (input == "describe") {
                   reply = "describing . {...}";
               } else if (input == "activate") {
                   window.setInterval(function() {
                       counter += 1;
                       term.write("\x1b[1K\x1b[G\x1b[0;1m<\x1b[0;33m change module:value [" +
                       counter + ", {}]\r\n\x1b[0;1m> " + input);
                   }, 1000);
                   reply = "active";
               } else if (input == "read module:value") {
                   reply = "reply module:value [127, {\"t\": now}]";
               } else {
                   reply = "error . [\"I don't understand this yet.\"]";
               }
               term.write("\x1b[0;1m<\x1b[0;33m " + reply + "\r\n");
               term.write("\x1b[0;1m>\x1b[1;36m ");
               input = "";
           } else {
               input += data;
               term.write(data);
           }
       });
   }

   $(function() { openterm(); });
   </script>

   <div style="width: 40vw; height: 50vh; background-color: black; padding: 1em;
   line-height: 1.3em; border-radius: 10px">
   <div id="term" style=""></div>
   </div>
