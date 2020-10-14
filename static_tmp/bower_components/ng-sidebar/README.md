# Semantic-UI.ngSidebar
Semantic is a UI component framework based around useful principles from natural language. http://www.semantic-ui.com

<p>
  <a href="https://gitter.im/miamarti/Semantic-UI.ngSidebar" target="_blank"><img src="https://img.shields.io/gitter/room/nwjs/nw.js.svg"></a>
  <img src="https://img.shields.io/badge/SemanticUI.ngSidebar-release-green.svg">
  <img src="https://img.shields.io/badge/version-1.0.1-blue.svg">
  <img src="https://img.shields.io/github/license/mashape/apistatus.svg">
  <a href="https://github.com/miamarti/Semantic-UI.ngSidebar/tarball/master"><img src="https://img.shields.io/github/downloads/atom/atom/latest/total.svg"></a>
  <img src="https://img.shields.io/bower/v/bootstrap.svg">
</p>

<img src="https://c5.staticflickr.com/9/8782/27626205084_2f5de3a37f_z.jpg" width="361" height="549" alt="Semantic-UI.ngSidebar">

## Dependencies
* AngularJS

## Implementation
```
<div class="ui right vertical inverted sidebar menu" id="toc" ng-sidebar=".btnSidebar">
    <div ng-include="'views/menu.html'"></div>
</div>
```

## Bower install de dependency
```
$ bower install Semantic-UI.ngSidebar --save
```

## Module AngularJS include
```
angular.module('example', ["ngSidebar"]);
```
