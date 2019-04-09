var express = require('express');
var galleryRouter = express.Router();

var router = function(title) {

    //galleryController를 가져옴
    var galleryController =
        require('../controllers/galleryController')(title);
    //현재위치 (https://url/)에서 get으로 request
    //Controller의 getGalleryImages함수 호출
    galleryRouter.route('/')
        .get(galleryController.getGalleryImages);

    return galleryRouter;
};
//app.js에서 해당 모듈을 require하여 사용할수있게 export
module.exports = router;