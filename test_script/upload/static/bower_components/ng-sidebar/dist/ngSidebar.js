(function () {
    'use strict';
    (angular.module('ngSidebar', ['ng'])).directive('ngSidebar', function () {
        return {
            restrict: 'A',
            link: function (scope, elem, attr) {
                $(elem).sidebar({
                    dimPage: true,
                    transition: 'push',
                    mobileTransition: 'uncover'
                });
                setTimeout(function () {
                    $(elem).sidebar('attach events', attr.ngSidebar);
                }, 1000);
            }
        };
    });
})(window, document);
