#include "cv.h"
#include "highgui.h"

#include <iostream>

using namespace std;

// Constants
int KEY_ESC = 27;
string WINDOW_MAIN = "Camera";
string WINDOW_INFO = "Information";
string WINDOW_PROCESSED = "Processed image";
cv::Scalar COLOR_BLACK = cv::Scalar::all( 0 );
cv::Scalar COLOR_RED = cv::Scalar( 0, 0, 255 );
cv::Scalar COLOR_GREEN = cv::Scalar( 0, 255, 0 );

// Functions
int getCameraIndex( int argc, const char** argv );
int convertStringToInt( string str );
void drawCircle( cv::Vec3f circle, cv::Mat img );
void writeCirclesInfo( vector<cv::Vec3f> circles, cv::Mat img );

int main( int argc, const char** argv )
{
    cv::VideoCapture capture( getCameraIndex( argc, argv ) );

    if ( !capture.isOpened() )
    {
        cerr << "ERROR: Could not capture image from camera" << endl;
        return -1;
    }

    cv::namedWindow( WINDOW_MAIN, 1 );
    cv::namedWindow( WINDOW_INFO, 1 );
    //cv::namedWindow( WINDOW_PROCESSED, 1 );

    while ( true )
    {
        cv::Mat img, processedImg, info( 320, 320, CV_32FC3, COLOR_BLACK );
        vector<cv::Vec3f> circles;

        capture >> img;
        img.copyTo( processedImg );
        cv::cvtColor( img, processedImg, CV_BGR2GRAY );
        cv::GaussianBlur( processedImg, processedImg, cv::Size( 7, 7 ), 1.5, 1.5 );

        cv::HoughCircles( processedImg, circles, CV_HOUGH_GRADIENT, 2, 
                          processedImg.rows / 4, 200, 100 );

        for ( int i = 0; i < circles.size(); i++ )
            drawCircle( circles[i], img );

        writeCirclesInfo( circles, info );

        cv::imshow( WINDOW_MAIN, img );
        cv::imshow( WINDOW_INFO, info );
        //cv::imshow( WINDOW_PROCESSED, processedImg );

        if ( cv::waitKey(10) == KEY_ESC )
            break;
    }

    return 0;
}

int getCameraIndex( int argc, const char** argv )
{
    int cameraIndex = 0;

    // See if the user has provided a different camera index as a command line argument
    if ( argc > 1 )
    {
        try 
        {
            cameraIndex = convertStringToInt( argv[1] );
        }
        catch ( string exception )
        {
            cerr << "ERROR: You have to provide a number for the camera index!" << endl;
            exit( 1 );
        }
    }

    return cameraIndex;
}

int convertStringToInt( string str )
{
    stringstream stream( str );
    int number;
    stream >> number;

    if ( !stream )
        throw "Could not convert string to int!";

    return number;
}

void drawCircle( cv::Vec3f circle, cv::Mat img )
{
    cv::Point center( circle[0], circle[1] );
    int radius = circle[2];

    // Draw the circle center
    cv::circle( img, center, 3, COLOR_GREEN, -1, 8, 0 );

    // Draw the circle outline
    cv::circle( img, center, radius, COLOR_RED, 3, 8, 0 );
}

void writeCirclesInfo( vector<cv::Vec3f> circles, cv::Mat img )
{
    int fontFace = cv::FONT_HERSHEY_SIMPLEX;
    double fontScale = .5;
    cv::Scalar color = COLOR_GREEN;
    int yPos = 40;
    int circlesCount = circles.size();
    stringstream stream;

    stream << circlesCount << " circles detected at:";
    cv::putText( img, stream.str(), cv::Point( 10, 20 ), fontFace, fontScale, color);

    for ( int i = 0; i < circlesCount; i++ )
    {
        stringstream stream;
        cv::Vec3f circle = circles[i];

        stream << i + 1 << ": " << circle[0] << ", " << circle[1];
        cv::putText( img, stream.str(), cv::Point( 30, yPos ), fontFace, fontScale, color);

        yPos += 20;
    }
}
