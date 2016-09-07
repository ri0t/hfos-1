'use strict';

class wikicomponent {
    
    constructor($scope, objectproxy, $state, $rootScope, stateparams, user, alert) {
        this.$scope = $scope;
        this.op = objectproxy;
        this.state = $state;
        this.rootscope = $rootScope;
        this.alert = alert;
        
        this.pagename = stateparams.name;
        this.pageuuid = "";
        
        this.title = 'No page';
        this.html = '<h1>Page not found</h1>';
        
        this.selectedtemplate = "Empty";
        
        var self = this;
        console.log('WIKI RUNNING');
        
        this.getData = function () {
            console.log('[WIKI] Getting wikipage');
            self.op.getObject('wikipage', null, true, {'name': self.pagename});
            self.op.getList('wikitemplate');
        };
        
        if (user.signedin) {
            console.log('[WIKI] Logged in, fetching page.')
            this.getData();
        }
        
        this.$scope.$on('User.Login', self.getData);
        
        this.$scope.$on('OP.List', function (ev, schema) {
            if (schema === 'wikitemplate') {
                self.templatelist = self.op.lists.wikitemplate;
                console.log('self.templatelist', self.templatelist);
            }
        });
        
        this.$scope.$on('OP.Get', function (ev, uuid, obj, schema) {
            console.log('[WIKI] UUID, OBJ, SCH', uuid, obj, schema);
            if (schema === 'wikipage') {
                console.log('[WIKI] Got a wikipage: ', obj, 'looking for:', self.pagename);
                if (obj.name == self.pagename) {
                    console.log('[WIKI] Got a wikipage!');
                    console.log('Wikicomponent got a wikipage!');
                    self.html = obj.html;
                    self.title = obj.title;
                    self.pageuuid = obj.uuid;
                    
                    var brackets = /\[([^\]]+)]/g;
                    self.html = self.html.replace(brackets, '<a href="#/wiki/$1">$1</a>');
                } else {
                    console.log('[WIKI] Not our page.');
                }
            } else if (schema === 'wikitemplate') {
                self.templates[obj.name] = obj;
            }
        })
    }
    
    createPage() {
        console.log('Creating empty page with name:', this.pagename, this.selectedtemplate);
/*        if (this.selectedtemplate == 'Empty') {
            this.state.go('app.editor', {schema: 'webpage', action: 'create'})
        } else {
            this.alert.add('warning', 'WiP', 'Sorry, this is Work in Progress.', 2);
        }
        */
        
    }
    
    editpage() {
        this.state.go('app.editor', {schema: 'wikipage', action: 'edit', uuid: this.pageuuid})
    }
}

wikicomponent.$inject = ['$scope', 'objectproxy', '$state', '$rootScope', '$stateParams', 'user', 'alert'];

export default wikicomponent;