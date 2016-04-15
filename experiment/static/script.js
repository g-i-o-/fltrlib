angular.module('roi-experiment-app', ['spectrogram-viewer', 'a2-directives', 'testapp'])
.run(function(){
    $(document).on('click', function(e){
        if($(e.target).closest('.dropdown.no-self-close:visible').length)
            return;

        $('.dropdown.no-self-close .dropdown-menu:visible').hide();
    });
})
.service('a2RoiExperimentService', function($http){
    return {
        getAlgorithms : function(){
            return $http.get('/algorithms');
        },
        getRecordingsData : function(){
            return $http.get('/recording/list');
        },
        getRecordingValidation : function(recording){
            return $http.get('/recording/' + ((recording && recording.id) | 0) + '/validation');
        },
        getRecordingAnnotations : function(recording, algorithm){
            return $http.get('/recording/' + ((recording && recording.id) | 0) + '/annotation/'+algorithm+'/list');
        },
        getRecordingOutputInfo : function(recording, algorithm){
            return $http.get('/recording/' + encodeURIComponent((recording && recording.file) || '') + '/output/'+algorithm);
        },
        annotateRecording : function(recording, label, algorithm){
            return $http.post('/recording/' + ((recording && recording.id) | 0) + '/annotation/'+algorithm, {label:label});
        }
    };
})
.filter('recordingImageUrl', function(){
    return function(recording, image, algorithm){
        return '/recording/' + encodeURIComponent((recording && recording.file) || '') + '/image/' + algorithm + '/' + encodeURIComponent(image || '') + '.png';
    };
})
.controller('a2RoiExperimentController',function(a2RoiExperimentService){
    var self=this;
    this.selected_rec = null;
    this.recoutput={};
    this.recoutputs_by_alg={};
    this.annotations = ["hit", "noval agree", "noval disagree", "roi miss"];
    this.selected_annotation = this.annotations[0];
    var get_closest_annotation = function(roi, annotations){
        var min_dist = 0, min_ann;
        var t0 = roi.t0, t1 = roi.t1, f0 = roi.f0, f1 = roi.f1;
        var mt = (t1+t0)/2, mf = (f1+f0)/2;
        var mw = (t1-t0)/2, mh = (f1-f0)/2;
        annotations.forEach(function(ann){
            var dt = (ann.t - mt) / mw, df = (ann.f - mf) / mh;
            var dist = Math.pow(dt*dt + df*df, 0.5);
            if( !min_ann || dist < min_dist){
                min_dist = dist;
                min_ann  = ann;
            }
        });
        return min_ann;
    };

    var fill_recoutput = function(recoutput, recid, algorithm){
        if(recoutput[recid]){
            return;
        }
        var recording = self.recordings[recid];
        a2RoiExperimentService.getRecordingOutputInfo(recording, algorithm).success(function(recording_info){
            recording_info.images.sort(function(a, b){
                var da = a.split('-').length, db = b.split('-').length;
                return da > db ? -1 : (db > da ? 1 : ( a> b ? -1 : (b > a ? 1 : 0)));
            })
            recording_info.current_image = recording_info.images[0];
            recording_info.show_rois=true;
            a2RoiExperimentService.getRecordingValidation(recording).success(function(validation){
                recording_info.validation = validation;
                recording_info.show_validation=true;
                a2RoiExperimentService.getRecordingAnnotations(recording, algorithm).success(function(annotations){
                    recording_info.annotations = annotations;
                    recording_info.show_annotations=true;
                    recording_info.show_annotation_type = {
                        'hit' : true,
                        'noval agree' : true,
                        'noval disagree' : true,
                        'miss' : true
                    };
                    recoutput[recid]=[recording_info];

                    recording_info.show_links=true;
                    recording_info.links = [];
                    recording_info.rois.forEach(function(roi){
                        roi.annotation = get_closest_annotation(roi, annotations);
                        var t0 = roi.t0, t1 = roi.t1, f0 = roi.f0, f1 = roi.f1;
                        var mt = (t1+t0)/2, mf = (f1+f0)/2;
                        recording_info.links.push([{t:mt, f:mf}, roi.annotation]);
                    });



                })
            })
        })
    };
    this.annotate = function(recording, label, t, f, algorithm){
        var annotation = {t:t, f:f, text:label};
        a2RoiExperimentService.annotateRecording(recording, annotation, algorithm).success(function(){
            self.recoutput[recording.id][0].annotations.push(annotation);
        });
    }
    this.selectRec = function(recid){
        self.selected_rec = recid;
        fill_recoutput(self.recoutput, recid, self.selected_algorithm);
    }
    this.selectAlgorithm = function(algorithm){
        self.selected_algorithm = algorithm;
        var last_ro = self.recoutput;
        if(!self.recoutputs_by_alg[algorithm]){
            self.recoutputs_by_alg[algorithm] = {};
        }
        self.recoutput = self.recoutputs_by_alg[algorithm];
        if(last_ro){
            for(var recid in last_ro){
                fill_recoutput(self.recoutput, recid, self.selected_algorithm);
            }
        }
    }
    a2RoiExperimentService.getAlgorithms().success(function(algorithms){
        self.algorithms = algorithms;
        a2RoiExperimentService.getRecordingsData().success(function(recordings){
            self.recordings=recordings;
            self.selectAlgorithm(algorithms[algorithms.length-1]);
        });
    });
})
.directive('roiExperiment', function(){
    return {
        restrict:'E',
        controller:'a2RoiExperimentController as ctrl',
        templateUrl:'/static/partials/roi-experiment.html'
    };
});


angular.module('spectrogram-viewer', [])
.service('sectrogramLayoutService', function(){
    var l=function(){};
    l.prototype={
        w:10378, h:257,
        sr : 44100, maxf: 22050, dur: 60.25,
        pps: 10378 / 60.25,
        pph: 257 / 22050.0,
        set : function(sr, dur){
            this.sr = sr;
            this.maxf = sr/2.0;
            this.dur = dur;
            this.w = (this.pps * dur) | 0;
            this.h = (this.pph * this.maxf) | 0;
        },
        sec2Px : function(sec, round){ var x=this.pps * sec; return round ? (x|0) : x;},
        hz2Px  : function( hz, round){ var y=this.pph *  hz; return this.h - (round ? (y|0) : y);},
        dsec2Px : function(dsec, round){ var x=this.pps * dsec; return round ? (x|0) : x;},
        dhz2Px  : function(dhz, round){ var y=this.pph *  dhz; return (round ? (y|0) : y);},
        px2sec  : function(px, round){ var x=px / this.pps; return round ? (x|0) : x;},
        px2hz   : function(py, round){ var y=(this.h - py) / this.pph; return (round ? (y|0) : y);},
        px2dsec : function(dpx, round){ var x=dpx / this.pps; return round ? (x|0) : x;},
        px2dhz  : function(dpy, round){ var y=dpy / this.pph; return (round ? (y|0) : y);}
    };
    return l;
})
.service('$templateGet', function($http, $sce, $templateCache, $q){
    return function(templateUrl){
        return $http.get($sce.getTrustedResourceUrl(templateUrl), {cache: $templateCache});
    };
})
.directive('spectrogramViewer', function(sectrogramLayoutService, $templateGet, $compile, $parse){
    return {
        restrict:'E',
        scope: {
            recording:'&',
            image:'@'
        },
        // templateUrl:'/static/partials/spectrogram-viewer.html',
        compile: function(element, attrs){
            var sets=[];
            element.children().each(function(i, chel){
                var at={};
                for(var ats=chel.attributes,ai=0,ae=ats.length; ai < ae; ++ai){
                    at[ats[ai].name] = ats[ai].value;
                }
                at.name = chel.nodeName.toLowerCase();
                sets.push(at);
            });
            element.empty();

            var ngclick = attrs.whenClick && $parse(attrs.whenClick);
            delete attrs.ngClick;

            return function(scope, element, attrs){
                $templateGet('/static/partials/spectrogram-viewer.html').success(function(template){
                    element.append($compile(template)(scope));
                    if(ngclick){
                        element.find('.spectrogram-container').click(function(evt){
                            var r = this.getBoundingClientRect();
                            var x = evt.clientX - r.x + this.scrollLeft, y = evt.clientY - r.y + this.scrollTop;
                            var t = scope.layout.px2sec(x), f = scope.layout.px2hz(y);
                            evt.t = t;
                            evt.f = f;
                            ngclick(tscope, {$event:evt});
                        })
                    }
                })
                scope.layout = new sectrogramLayoutService();
                scope.sets={rois:[], labels:[], links:[]};
                var tscope = scope.$parent.$new();
                sets.forEach(function(setdef, i){
                    var set, setset = scope.sets[setdef.name];
                    setset.push(set = {idx:setset.length});
                    tscope.$watch(setdef.data, function(data){
                        set.data = data;
                    });
                });
                scope.$on('$destroy', function(){
                    tscope.$destroy();
                });

                scope.$watch('recording()', function(recording){
                    if(!recording) return;
                    scope.layout.set(recording.sample_rate, recording.duration)
                });
            }
        }
    }
})
.directive('spectrogramElement', function(sectrogramLayoutService, $templateGet, $compile, $parse){
    return {
        restrict:'E',
        compile: function(element, attrs){
            return function(scope, element, attrs){
            }
        }
    }
});


angular.module('a2-directives', [])
.directive('a2GlobalKeyup', function($window, $timeout){
    var $ = $window.$;

    return {
        restrict : 'A',
        scope : {
            onkeyup:'&a2GlobalKeyup'
        }, link: function($scope, $element, $attrs){

            var handler = function(evt){
                $timeout(function(){
                    $scope.onkeyup({$event:evt});
                });
            };
            $(document).on('keyup', handler);
            $element.on('$destroy', function() {
                $(document).off('keyup', handler);
            });
        }
    };
})
.filter('charCode', function(){
    return function(code){
        return String.fromCharCode(code);
    };
})
.directive('noSelfClose', function(){
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            element.on('click', function(e){
                e.stopPropagation();
                // e.preventDefault();
            });
        }
    };
})
;


angular.module('testapp',[])
.directive('statesgraphU', function(){
    return {
        restrict:'E',
        controller:'UsStates',
        template:
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xl="http://www.w3.org/1999/xlink" version="1.1" width="1200" height="180" xmlns:dc="http://purl.org/dc/elements/1.1/">' +
          '<g stroke="none" stroke-opacity="1" stroke-dasharray="none" fill="none" fill-opacity="1">' +
            '<g>' +
              '<rect ng-repeat="state in states | orderBy:order" ng-attr-x="{{2+($index *16)}}" ng-attr-y="{{170 - (state.inc/10)}}" width="14" ng-attr-height="{{state.inc/10}}" fill="#F0F8FF" stroke="black" stroke-linecap="round" stroke-linejoin="round" stroke-width="1">' +
                '<title>{{state.inc}}</title>' +
              '</rect>' +
              '<line ng-repeat="state in states | orderBy:order"' +
                'ng-attr-x1="{{2+($index *16)}}"' +
                'ng-attr-y1="{{170 - (state.inc/10)}}"' +
                'ng-attr-x2="{{2+($index *16) + 14}}"' +
                'ng-attr-y2="{{170 - (state.inc/10) + state.inc/10}}"' +
                'fill="#F0F8FF" stroke="black" stroke-linecap="round" stroke-linejoin="round" stroke-width="1">' +
            '</line>' +
              '<text ng-repeat="state in states | orderBy:order" ng-attr-transform="{{ \'translate(\' + (12 + ($index *16)) + \' 165) rotate(-90)\' }}" fill="black">' +
                '<tspan font-family="Helvetica Neue" font-size="11" font-weight="500">{{state.name}}</tspan>' +
              '</text>' +
            '</g>' +
          '</g>' +
        '</svg>'
    };
})
.controller('UsStates',
function UsStates($scope, $log) {

    $scope.order = "name";

    $scope.states = [
        { name: "Louisiana", "inc" : 1619},
        { name: "Alabama", "inc" : 735},
        { name: "Oklahoma", "inc" : 661},
        { name: "Texas", "inc" : 639},
        { name: "Mississippi", "inc" : 634},
        { name: "Arizona", "inc" : 567},
        { name: "Florida", "inc" : 557},
        { name: "Georgia", "inc" : 540},
        { name: "South Carolina", "inc" : 519},
        { name: "Alaska", "inc" : 511},
        { name: "Missouri", "inc" : 509},
        { name: "Kentucky", "inc" : 492},
        { name: "Virginia", "inc" : 489},
        { name: "Michigan", "inc" : 488},
        { name: "Nevada", "inc" : 486},
        { name: "Idaho", "inc" : 474},
        { name: "California", "inc" : 467},
        { name: "Colorado", "inc" : 467},
        { name: "Delaware", "inc" : 463},
        { name: "Ohio", "inc" : 449},
        { name: "Indiana", "inc" : 442},
        { name: "Tenassee", "inc" : 436},
        { name: "Arkansas", "inc" : 430},
        { name: "South Dakota", "inc" : 412},
        { name: "Connecticut", "inc" : 407},
        { name: "Maryland", "inc" : 403},
        { name: "Wisconsin", "inc" : 393},
        { name: "Wyoming", "inc" : 387},
        { name: "Wisconsin", "inc" : 374},
        { name: "Oregan", "inc" : 371},
        { name: "Montana", "inc" : 368},
        { name: "North Carolina", "inc" : 368},
        { name: "Illinois", "inc" : 351},
        { name: "Hawaii", "inc" : 332},
        { name: "West Virginia", "inc" : 331},
        { name: "New Mexico", "inc" : 316},
        { name: "New York", "inc" : 307},
        { name: "Kansas", "inc" : 303},
        { name: "New Jersey", "inc" : 298},
        { name: "Iowa", "inc" : 291},
        { name: "Washington", "inc" : 272},
        { name: "Vermont", "inc" : 260},
        { name: "Nebraska", "inc" : 247},
        { name: "Rhode Island", "inc" : 240},
        { name: "Utah", "inc" : 232},
        { name: "North Dakota", "inc" : 225},
        { name: "New Hampshire", "inc" : 220},
        { name: "Massachusetts", "inc" : 218},
        { name: "Minnesota", "inc" : 179},
        { name: "Maine", "inc" : 151}
        ];
}
)
;
