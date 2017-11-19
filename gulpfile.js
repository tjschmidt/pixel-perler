var gulp = require('gulp');
var clean = require('gulp-clean');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');
var cssmin = require('gulp-clean-css');
var sass = require('gulp-sass');
var plumber = require('gulp-plumber');
var ts = require('gulp-typescript');
var tsProject = ts.createProject('tsconfig.json');

var projName = 'pixel-perler';

var srcDir = './web/src/';
var buildDir = './build';
var destDir = './python/core/static/';

var jsGlob = srcDir + 'ts/*.ts';
var cssGlob = srcDir + 'scss/*.scss';

gulp.task('clean', function () {
    return gulp.src(buildDir, {read: false})
        .pipe(clean());
});

gulp.task('js', function () {
    return gulp.src(jsGlob)
        .pipe(plumber())
        .pipe(tsProject())
        .pipe(gulp.dest(buildDir))
        .pipe(rename(projName + '.min.js'))
        .pipe(uglify())
        .pipe(gulp.dest(destDir + 'js/'));
});

gulp.task('css', function () {
    return gulp.src(cssGlob)
        .pipe(plumber())
        .pipe(sass())
        .pipe(gulp.dest(buildDir))
        .pipe(cssmin())
        .pipe(rename(projName + '.min.css'))
        .pipe(gulp.dest(destDir + 'css/'));
});

gulp.task('dist', ['js', 'css'], function () {
});
// gulp.task('dist', ['css'], function () {
// });

gulp.task('default', function () {
});

gulp.watch(cssGlob, ['css']);
gulp.watch(jsGlob, ['js']);
