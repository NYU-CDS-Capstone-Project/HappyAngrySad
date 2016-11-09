$(document).ready(function() {
    var isChrome = !!window.chrome && !!window.chrome.webstore;
    var isFirefox = typeof InstallTrigger !== 'undefined';
    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    
    if (isChrome || isFirefox || isOpera) {
        JSSDKDemo.init();
        JSSDKDemo.run();
    } else {
        JSSDKDemo.create_alert("incompatible-browser", "It appears that you are using an unsupported browser. Please try this demo on Chrome, Firefox, or Opera.");
    }
});

var JSSDKDemo = (function() {
    var detector = null;
    var capture_frames = false;
    var ready_to_accept_input = true;
    var finished_watching = false;
    var processed_frames = [ [], [], [], [], [] ];
    var frames_since_last_face = 0;
    var face_visible = true;

    var player = null;
    var VIDEO_HEIGHT = 510;
    var VIDEO_WIDTH = 853;
    var VIDEO_VOLUME = 50;
    var VIDEO_LENGTH_THRESHOLD = 5;
    var video_duration_sec = 0;
    var video_duration_ms = 0;
    var video_cutoff_sec = 0;
    var start_time = 0;
    var stop_time = 0;
    var playing = false;
    
    var stop_capture_timeout = null;
    var time_left_sec = 0;
    var time_buffering_ms = 0;
    var buffer_start_time_ms = 0;

    var emotions = ["joy", "anger", "disgust", "contempt", "surprise"];
    var colors = ["#FFFFFF", "orangered", "deeppink", "yellow", "green"];
    var selected_emotion = "all";
    var svg_width = 720;
    var x_scale = d3.scale.linear().domain([0, 0]).range([0, svg_width]);
    var y_scale = d3.scale.linear().domain([100, 0]).range([2, 248]);
    var t = null;
    var cursor_interval = null;
    
    var API_KEY = "AIzaSyCdQbLORhF7PGVJ7DG1tkoVJGgDYwA_o0M";

    var video_id = "Pc7BnT5X1tw";

    let lastPostToServerTime = 0;

    let view_id = null;

    let currentAggregate = null;
    let totalFrames = 0;
    let framesSkipped = 0;

    var resetAggregate = function () {
        totalFrames = 0;
        framesSkipped = 0;
        currentAggregate = null;
    }

    var postAggregate = function() {
        if (currentAggregate == null) {
            return;
        }

        const numFrames = totalFrames - framesSkipped;

        for (let key in currentAggregate.emotions) {
            if (currentAggregate.emotions.hasOwnProperty(key)) {
                currentAggregate.emotions[key] /= numFrames
            }
        }
        for (let key in currentAggregate.emojis) {
            if (currentAggregate.emojis.hasOwnProperty(key)) {
                currentAggregate.emojis[key] /= numFrames
            }
        }        
        currentAggregate['totalFrames'] = totalFrames
        currentAggregate['framesSkipped'] = framesSkipped

        $.ajax({
            url: "/postFaces",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ 
                faces: currentAggregate,
                view_id: view_id
            }),
            success: function() {},
            error: function (jqXHR, textStatus, errorThrown)
            {
                console.log("failed to post to server");
            },                    
        });

        resetAggregate();
    }

    var run = function() {
        var facevideo_node = document.getElementById("facevideo-node");
        detector = new affdex.CameraDetector(facevideo_node);
        
        // classes of data we can get
        detector.detectAllEmotions();
        detector.detectAllEmotions();
        detector.detectAllEmojis();
        detector.detectAllAppearance();

        detector.addEventListener("onWebcamConnectSuccess", function() {
            show_message("msg-starting-webcam");
        });
        
        detector.addEventListener("onWebcamConnectFailure", function() {
            show_message("msg-webcam-failure");
        });
        
        if (detector && !detector.isRunning) {
            detector.start();
        }
        
        // get the video element inside the div with id "facevideo-node"
        var face_video = $("#facevideo-node video")[0];
        face_video.addEventListener("playing", function() {
            show_message("msg-detector-status");
        });
        
        detector.addEventListener("onInitializeSuccess", function() {
            // show_message("instructions");
            var video_id = "Pc7BnT5X1tw";
            player.loadVideoById(video_id, 0);

            console.log(player);
                
            resetAggregate();
                
            $.ajax({
                url: "/startView",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ 
                    video_id: video_id,
                }),
                success: function(data, textStatus, jqXHR)
                {
                    console.log("Created new view: " + data);
                    view_id = data;
                },
                error: function (jqXHR, textStatus, errorThrown)
                {
                    console.log("fail: " + textStatus);
                },                    
            });
        });
        
        detector.addEventListener("onImageResultsSuccess", function(faces, image, timestamp) {
            totalFrames++;
            if (view_id != null && faces.length == 1) {
                const face = faces[0];
                if (currentAggregate == null) {
                    currentAggregate = {
                        emotions: face.emotions,
                        emojis: face.emojis,
                        appearance: face.appearance,
                    }
                } else {
                    for (let key in face.emotions) {
                        if (face.emotions.hasOwnProperty(key)) {
                            currentAggregate.emotions[key] += face.emotions[key];
                        }
                    }
                    for (let key in face.emojis) {
                        if (face.emojis.hasOwnProperty(key)) {
                            currentAggregate.emojis[key] += face.emojis[key];
                        }
                    }
                }
                delete currentAggregate.emojis.dominantEmoji;
            } else {
                framesSkipped++;
            }


            if (Date.now() > lastPostToServerTime + 5000) {
                postAggregate();
                lastPostToServerTime = Date.now();
            }

            // get the time as close to the actual time of the frame as possible
            //  account for time spent buffering
            var fake_timestamp = get_current_time_adjusted();            

            if (capture_frames) {
                if (frames_since_last_face > 100 && face_visible) {
                    face_visible = false;
                    create_alert("no-face", "No face was detected. Please re-position your face and/or webcam.");
                }
                
                if (faces.length > 0) {
                    if (!face_visible) {
                        face_visible = true;
                        fade_and_remove("#no-face");
                        $("#lightbox").fadeOut(1000);
                    }
                    frames_since_last_face = 0;
                    emotions.forEach(function(val, idx) {
                        processed_frames[idx].push([fake_timestamp, faces[0].emotions[val]]);
                    });
                } else {
                    frames_since_last_face++;
                    emotions.forEach(function(val, idx) {
                        processed_frames[idx].push([fake_timestamp, 0]);
                    });
                }
                update_plot();
            }
        });
    };

    // var start_button_click = function(event) {
    //     $(".demo-message").hide();
        
    //     if (ready_to_accept_input) {
    //         ready_to_accept_input = false;
    //         var video_id = ytvidid;
            
    //         if (event.data == null) {
    //             var blob = document.getElementById("start-form").value;
                
    //             if (blob === "" || blob.includes("http://") || blob.includes("https://")) { // treat as URL
    //                 video_id = blob.split("v=")[1] || "";
    //                 var ampersandPosition = video_id.indexOf("&");
    //                 if (ampersandPosition !== -1) {
    //                     video_id = video_id.substring(0, ampersandPosition);
    //                 }
    //             } else { // treat as search
    //                 var url = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key=" + API_KEY + "&maxResults=10&safeSearch=strict&q=" + blob;
    //                 http_get_async(url, add_to_search_results);
    //             }
                
    //         } else { // play the video that was clicked
    //             video_id = event.data.id;
    //         }
            
    //         if (typeof video_id !== "undefined") {
                
    //             player.loadVideoById(video_id, 0);
                
    //             resetAggregate();
                
    //             $.ajax({
    //                 url: "/startView",
    //                 type: "POST",
    //                 contentType: "application/json",
    //                 data: JSON.stringify({ 
    //                     video_id: video_id,
    //                 }),
    //                 success: function(data, textStatus, jqXHR)
    //                 {
    //                     console.log("Created new view: " + data);
    //                     view_id = data;
    //                 },
    //                 error: function (jqXHR, textStatus, errorThrown)
    //                 {
    //                     console.log("fail: " + textStatus);
    //                 },                    
    //             });
    //         }
    //     }
    // };
    
    var begin_capture = function() {
        // take care of gap at beginning
        x_scale = d3.scale.linear().domain([start_time, start_time + video_duration_ms]).range([0, svg_width]);
        emotions.forEach( function(val, idx) {
            processed_frames[idx].push([start_time, 0]);
        });
        update_plot();
        
        capture_frames = true;
        
        $("#demo-setup").fadeOut("fast", function() {
            $("#video-container").show();
            init_plot();
            stop_capture_timeout = setTimeout(stop_capture, video_duration_ms);
        });
    };
    
    var stop_capture = function() {
        stop_time = get_current_time_adjusted();
        capture_frames = false;
        detector.stop();
        $(".alert").hide();
        
        // focus on message
        $("#lightbox").fadeIn(750, function() {
            // render cursor
            add_cursor();
            track_video();
            
            // make emotion buttons and player clickable
            //$("#ul-wrapper").css("pointer-events", "");
            $("#player").css("pointer-events", "");
            
            $("#play-again").fadeIn(500, function() {
                $("#lightbox").one("click", transition_to_playback);
            });
        });
    };
    
    var track_video = function() {
        cursor_interval = setInterval(function() {
            if (playing) {
                var x_coord = t(player.getCurrentTime());
                translate_cursor(x_coord);
            }
        }, 50);
    };
    
    var add_cursor = function() {
        // drag and drop
        var curve = d3.select("#svg-curve");
        var drag_group = curve.append("svg:g").attr("y1", 0).attr("y2", 250).attr("x1", 0).attr("x2", 10).attr("class", "draggable-group");
        drag_group.append("svg:rect").attr("x", -5).attr("y", 0).attr("width", 10).attr("height", 250).attr("class", "draggable-rect");
        drag_group.append("svg:line").attr("class", "cursor cursor-wide").attr("y1", 0).attr("y2", 250).attr("x1", 0).attr("x2", 0);

        drag_group.call(d3.behavior.drag().on("drag", function() {
            var x_coord = d3.event.x;
            var playback_time = t.invert(x_coord);
            
            if (playback_time < 0) {
                x_coord = 0;
                playback_time = 0;
            } else if (playback_time >= video_cutoff_sec) {
                playback_time = video_cutoff_sec - 0.001;
                x_coord = t(playback_time);
            }
            
            translate_cursor(x_coord);
            player.seekTo(playback_time);
            
        }).on("dragstart", function(event) {
            if (playing) {
                clearInterval(cursor_interval);
            }
            $("html, .draggable-rect, line.cursor-wide").css({"cursor": "-webkit-grabbing"});
            $("html, .draggable-rect, line.cursor-wide").css({"cursor": "-moz-grabbing"});
            $("html, .draggable-rect, line.cursor-wide").css({"cursor": "grabbing"});
        }).on("dragend", function() {
            if (playing) {
                track_video();
            }
            $("html").css({"cursor": "default"});
            $(".draggable-rect, line.cursor-wide").css("cursor", "pointer");
        }));

        curve.append("svg:text").attr("class", "time video_current_time").attr("y", 20).attr("x", 5).text("0:00");
        curve.on("click", svg_click);
    };

    var svg_click = function() {
        var x_click = d3.mouse(this)[0];
        var playback_time = t.invert(x_click);
        
        if (playback_time >= video_cutoff_sec) {
            playback_time = video_cutoff_sec - 0.001;
            x_click = t(playback_time);
        }
        
        if (playing) {
            clearInterval(cursor_interval);
        }
        
        translate_cursor(x_click);
        player.seekTo(playback_time);
        
        if (playing) {
            track_video();
        }
    };
    
    var path = d3.svg.line().x(function(d, i) {
        return x_scale(d[0])
    }).y(function(d, i) {
        return y_scale(d[1])
    }).interpolate("basis");
    
    var init_plot = function() {
        var curve = d3.select("#svg-curve");

        var initial_data = [
            [ [0, 0] ], // joy
            [ [0, 0] ], // anger
            [ [0, 0] ], // disgust
            [ [0, 0] ], // contempt
            [ [0, 0] ]  // surprise
        ];

        curve.selectAll("path.curve").data(initial_data)
        .enter().append("svg:path")
        .attr("class", "curve")
        .attr("id", function(d, i){return emotions[i]})
        .attr("d", path).attr("stroke", function(d, i) { return colors[i] } )
        .attr("fill", "transparent")
        .attr("stroke-width","2px")
        .attr("stroke-opacity", "1");
    };

    var update_plot = function(message) {
        var curve = d3.select("#svg-curve");
        curve.selectAll("path.curve").data(processed_frames)
            .attr("d", path);
    };

    var translate_cursor = function(x_coord) {
        // translate timeline cursor
        d3.selectAll("#svg-curve .draggable-group").attr("transform", "translate(" + x_coord + ", 0)");
        
        // render time
        var time = d3.selectAll("#svg-curve text.video_current_time");
        var time_sec = Math.floor(x_coord / svg_width * video_duration_sec);
        var text = text_time(time_sec);
        time.text(text);
        
        // figure out if flip is necessary
        $("#text-width")[0].innerHTML = text;
        var text_width = $("#text-width")[0].clientWidth;
        var flip_at = svg_width - text_width - 5;
        
        if (x_coord > flip_at) {
            time.attr("transform", "translate(" + (x_coord - text_width - 10) + ", 0)");
        } else {
            time.attr("transform", "translate(" + x_coord + ", 0)");
        }
    };
    
    var text_time = function(time_sec) {
        return Math.floor(time_sec / 60) + ":" + ((time_sec % 60 < 10) ? ("0" + time_sec % 60) : time_sec % 60);
    };

    var transition_to_playback = function() {
        $("#lightbox").fadeOut(500);
        $("#btn-play-again").fadeOut(500, function() {
            $(this).replaceWith(function() {
                return $("<button id='btn-play-again' class='btn btn-primary'>Try again</button>").fadeIn(500, function() {
                    document.onkeypress = function(event) {
                        if ((event || window.event).charCode == 32) {
                            if (playing) {
                                player.pauseVideo();
                            } else {
                                player.playVideo();
                            }
                        }
                    };

                    $("#btn-play-again").one("click", function() {
                        window.location.reload(false);
                    });
                });
            });
        });
    };
    
    var no_internet = function() {
        $(".alert").hide();
        create_alert("terminated", "It appears that you aren't connected to the Internet anymore. Please refresh the page and try again.");
    };
    
    var http_get_async = function(url, callback) {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                callback(xmlHttp.responseText);
            }
        };
        xmlHttp.open("GET", url, true);
        xmlHttp.send(null);
    };
    
    var add_to_search_results = function(text) {
        $("#search-results").empty();
        var results = JSON.parse(text);
        var list = results.items;
        
        // add results
        for (var i = 0; i < list.length; i++) {
            var v = list[i];
            var s = v.snippet;
            var id = v.id.videoId;
            
            var result = document.createElement("div");
            result.className = "list-group-item";
            result.innerHTML = '<table><tr><td><img class="thumbnail" id="' + id + '" src="' + s.thumbnails.medium.url + '" style="margin-right:15px"></td><td valign="top"><h3>' + s.title + '</h3><span>' + s.description + '</span></td></tr></table>';
            $("#search-results").append(result);
            // $("#"+id).click({id: id}, start_button_click);
        }
        
        // show a message for when no videos were found
        var num_videos = results.pageInfo.totalResults;
        if (num_videos === 0) {
            var message = document.createElement("div");
            message.className = "list-group-item";
            message.innerHTML = '<p>No results were found.</p>';
            $("#search-results").append(message);
        }
        
        // scroll to results
        $("html, body").animate({
            scrollTop: $("#search-results").offset().top - 15
        });
        
        ready_to_accept_input = true;
    };
    
    // var video_ids = ["ugo7Y2lRsxc", "Pc7BnT5X1tw", "IV_ef2mm4G0", "dlNO2trC-mk", "ugn_qmQ0NFo", "o2P5E7cFt9s"];
    
    // var populate_examples = function() {
    //     video_ids.forEach(function(element, index) {
    //         var id = "#example-" + index;
    //         var thumbnail_url = "https://i.ytimg.com/vi/" + video_ids[index] + "/mqdefault.jpg";
    //         $(id)[0].style.backgroundImage = "url(" + thumbnail_url + ")";
    //         $(id).click({id: video_ids[index]}, start_button_click);
            
    //         var url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + element + "&key=" + API_KEY;
    //         http_get_async(url, function(text) {
    //             var results = JSON.parse(text);
    //             var title = results.items[0].snippet.title;
    //             $(id).hover(function() {
    //                 this.style.backgroundBlendMode = "overlay";
    //                 $(this)[0].innerText = title;
    //             }, function(){
    //                 this.style.backgroundBlendMode = "initial";
    //                 $(this)[0].innerText = "";
    //             });
    //         });
    //     });
    // };


    var get_current_time_adjusted = function() {
        return Date.now() - time_buffering_ms;
    };
    
    var create_alert = function(id, text) {
        $("#lightbox").fadeIn(500);
        $("<div></div>", {
            id: id,
            class: "alert alert-danger",
            display: "none",
            text: text,
        }).appendTo("#lightbox");
        $("#" + id).css({"text-align": "center", "z-index": 2});
        $("#" + id).fadeIn(1000);
    };
    
    var show_message = function(id) {
        $(".demo-message").hide();
        $(document.getElementById(id)).fadeIn("fast");
    };
    
    var fade_and_remove = function(id) {
        $(id).fadeOut(500, function() {
            this.remove();
        });
    };
    
    
    
    return {
        init: function() {
            // $("#btn-start").click(start_button_click);
            $("#btn-play-again").one("click", transition_to_playback);
            
            // add click functionality to enter button
            $("#start-form").keyup(function(event) {
                if (event.keyCode === 13 || event.which === 13) {
                    $("#btn-start").click();
                }
            });
            
            // "show all" button
            $("#all").css("border", "3px solid #ffcc66");
            
            $("#all").click(function() {
                // set border
                if (selected_emotion !== "all") {
                    $("#" + selected_emotion).css("border", "");
                    $(this).css("border", "3px solid #ffcc66");
                }
                selected_emotion = "all";
                
                var curve = d3.select("#svg-curve");
                curve.selectAll("path.curve")
                    .transition()
                    .duration(400)
                    .attr("stroke-opacity", 1.0);
            });
            
            // populate sample videos
            // populate_examples();
            
            // load IFrame Player API code asynchronously
            setTimeout(function() {
                var tag = document.createElement("script");
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName("script")[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            }, 1000);
            
            // initialize player
            window.onYouTubeIframeAPIReady = function() {
                player = new YT.Player("player", {
                    height: VIDEO_HEIGHT,
                    width: VIDEO_WIDTH,
                    playerVars: {
                        "controls": 0,
                        "iv_load_policy": 3,
                        "rel": 0,
                        "showinfo": 0
                    },
                    events: {
                        "onError": onPlayerError,
                        "onStateChange": onPlayerStateChange
                    }
                });

                function onPlayerError(event) {
                    show_message("msg-bad-url");
                    player.stopVideo();
                    ready_to_accept_input = true;
                }

                function onPlayerStateChange(event) {
                    var status = event.data;
                    
                    if (!finished_watching) {
                        if (status === YT.PlayerState.PLAYING) {
                            video_duration_sec = player.getDuration();
                            
                            if (video_duration_sec > VIDEO_LENGTH_THRESHOLD) {
                                
                                if (start_time > 0) { // started playing again after buffering
                                    capture_frames = true;
                                    stop_capture_timeout = setTimeout(stop_capture, time_left_sec * 1000);
                                    
                                    // add how much time was spent buffering
                                    var buffer_time = Date.now() - buffer_start_time_ms;
                                    time_buffering_ms += buffer_time;
                                    
                                } else { // just started playing from the beginning
                                    start_time = Date.now();
                                    player.setVolume(VIDEO_VOLUME);
                                    video_duration_ms = video_duration_sec * 1000;
                                    video_cutoff_sec = Math.floor(video_duration_sec);
                                    t = d3.scale.linear().domain([0, video_duration_sec]).range([0, svg_width]);
                                    begin_capture();
                                }
                                
                            } else { // video loads and starts playing but is too short
                                show_message("msg-short-video");
                                player.stopVideo();
                                ready_to_accept_input = true;
                            }
                            
                        } else if (status === YT.PlayerState.BUFFERING && video_duration_sec > VIDEO_LENGTH_THRESHOLD) { // video is valid but needs to buffer
                            capture_frames = false;
                            clearTimeout(stop_capture_timeout);
                            time_left_sec = video_duration_sec - player.getCurrentTime();
                            
                            // log the time when buffering started
                            buffer_start_time_ms = Date.now();
                        }
                    }
                    
                    if (status === YT.PlayerState.ENDED) {
                        if (!finished_watching) {
                            finished_watching = true;
                        } else {
                            translate_cursor(0);
                        }
                        player.seekTo(0);
                        player.pauseVideo();
                        
                        if (view_id != null) {
                            postAggregate();

                            $.ajax({
                                url: "/finishView",
                                type: "POST",
                                contentType: "application/json",
                                data: JSON.stringify({ 
                                    view_id: view_id,
                                }),
                                success: function(data, textStatus, jqXHR)
                                {
                                    console.log("View has been finalized: " + data);
                                },
                                error: function (jqXHR, textStatus, errorThrown)
                                {
                                    console.log("fail: " + textStatus);
                                },                    
                            });
                            view_id = null;
                            
                            video_id = "t8IFgEO6Np4";
                            player.loadVideoById(video_id, 0);

                        } else {
                            console.log("Warning: view_id is null when video ended");
                        }
                    } else if (status === YT.PlayerState.CUED && video_duration_sec > VIDEO_LENGTH_THRESHOLD && !finished_watching) { // loss of Internet while playing video
                        finished_watching = true;
                        player.stopVideo();
                        clearTimeout(stop_capture_timeout);
                        detector.stop();

                        no_internet();
                    }
                    
                    // make cursor less buggy while video is paused
                    if (status === YT.PlayerState.PLAYING) {
                        playing = true;
                    } else {
                        playing = false;
                    }
                }
            };
        },

        run: run,

        responses: function(clicked_id) {
            // set border
            if (selected_emotion !== clicked_id) {
                $("#" + selected_emotion).css("border", "");
                $("#" + clicked_id).css("border", "3px solid #ffcc66");
            }
            selected_emotion = clicked_id;
            
            var curve = d3.select("#svg-curve");
            curve.selectAll("path.curve")
                .transition()
                .duration(400)
                .attr("stroke-opacity", function(d,i) {
                    if (this.id === clicked_id) {
                        return 1.0;
                    } else {
                        return 0.2;
                    }
                });
        },
        
        create_alert: create_alert
    };
})();
