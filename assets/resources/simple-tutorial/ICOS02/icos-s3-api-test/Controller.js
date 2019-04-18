var Controller = function(title) {
    var aws = require('aws-sdk'); //aws api를 사용하기위해 추가

    //s3프로토콜을 위한 정보 기입
    var ep = new aws.Endpoint('https://s3.us-south.cloud-object-storage.appdomain.cloud');
    var s3 = new aws.S3({
        endpoint: ep, 
        region: 'us-south',
        accessKeyId:'b01c551bb9604c8ebc22fefe36e4fbc7',
        secretAccessKey:'06d88e8c4d75adba1d51ce863144fe29b02d6fcb36c15f39'
    });

    //cos bucket name
    var myBucket = 'yourBucketName';


    var createBucket=function(req,res){
        //Bucket name should be unique
        var params = {Bucket: 'somethingNewName'};
        s3.createBucket(params, function(err,data) {
            if (err) {
             console.log("Error data: ", err);
            } else{
             console.log("checking for data "+ JSON.stringify(data));
            }
        });
    };

    var putObject=function(req,res){
        var params = {Bucket: myBucket, Key: 'name_toStore.txt', Body: require('fs').createReadStream('./filepath/filename.txt')};
        s3.putObject(params, function(err, data) {
          if (err) {
           console.log("Error data: ", err);
          } else {
           console.log("checking for data "+ JSON.stringify(data));
          }
         
        });
    };
    
    var listObject = function (req, res) {
        var params = {Bucket: myBucket};
        s3.listObjectsV2(params, function (err, data) {
            if (err) {
             console.log("Error data: ", err);
            } else{
             console.log("checking for data "+ JSON.stringify(data));
            }
        });
    };
    var delObject=function(req,res){
        var itemsToDelete = Array();
            itemsToDelete.push ({ Key : 'name_toDelete.txt' });
        var params = {Bucket: myBucket,
            Delete: {
                Objects: itemsToDelete,
                Quiet: false}};
        s3.deleteObjects(params, function(err, data) {
            if (err) {
             console.log("Error data: ", err);
            } else {
             console.log("checking for data "+ JSON.stringify(data));
            };
        });
    }
    var delBucket=function(req,res){
        var params={Bucket:myBucket};
        s3.deleteBucket(params, function(err, data) {
            if (err) {
                console.log("Error data: ", err);
               } else {
                console.log("checking for data "+ JSON.stringify(data));
               };
          });
    }
    return {
        createBucket: createBucket,
        listObject: listObject,
        upload: upload,
        putObject:putObject,
        delObject:delObject,
        delBucket:delBucket
    };
};

module.exports = Controller;


