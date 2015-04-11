/**
* WorldChat Module
*
* Description
*/
angular.module('WorldChat', []).
controller('MainController', [
    '$scope',
    '$http',

    function($scope, $http) {
        $scope.messages = [];
        $scope.myMessage = '';

        $scope.fetch = function() {

            console.log('STARTING...')

            $http.get('/fetch').
            success(function(data) {
                if(data.status == 1) {
                    $scope.messages.push(data.message.global_notifications);
                }
                $scope.fetch();

            }).
            error(function(data, status) {
                if (status != 0) {
                    console.log(data, status);
                    alert('Hey, something is veeeery wrong!');
                }
            });

        };

        $scope.sendMessage = function() {

            config = {};

            config.headers = {
                'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'
            };
            config.data = {'message': $scope.myMessage};
            config.method = 'POST';
            config.url = '/update';

            $http(config).then(function(data) {

                console.log(data);

            },
            function(data, status) {
                if (status != 0) {
                    console.log(data, status);
                    alert('Hey, something is veeeery wrong!');
                }
            });

        };

        $scope.fetch();
    }
]);