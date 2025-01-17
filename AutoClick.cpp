#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <print>
class auto_click final {
  private:
    char button_{};
    int click_{}, counter_{};
    DWORD sleep_time_{};
    auto execute_()
    {
        switch ( button_ ) {
            case 'L' : {
                mouse_event( MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP, 0, 0, 0, 0 );
                break;
            }
            case 'M' : {
                mouse_event( MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0 );
                break;
            }
            case 'R' : {
                mouse_event( MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0 );
                break;
            }
        }
    }
  public:
    auto_click()  = default;
    ~auto_click() = default;
    auto set( char _button, int _click, DWORD _sleep_time )
    {
        this->button_     = _button;
        this->click_      = _click;
        this->sleep_time_ = _sleep_time;
    }
    auto run()
    {
        for ( ; counter_ < click_; ++counter_ ) {
            execute_();
            Sleep( sleep_time_ );
        }
    }
};
auto main() -> int
{
    auto_click clicker;
    int click{};
    DWORD sleepTime{};
    char button[ 2 ]{};
    while ( true ) {
        std::print( "输入点击次数: " );
        while ( true ) {
            std::scanf( "%d", &click );
            if ( click > 0 ) {
                break;
            }
            std::print( "数据必须大于 0, 请重新输入: " );
        }
        std::print( "输入间隔时间 (单位: 毫秒): " );
        while ( true ) {
            std::scanf( "%lu", &sleepTime );
            if ( sleepTime > 0 ) {
                break;
            }
            std::print( "输入数据必须大于 0, 请重新输入: " );
        }
        std::print( "按下左键 (L), 中键 (M), 还是右键 (R): " );
        while ( true ) {
            std::scanf( "%s", button );
            if ( ( ( button[ 0 ] == 'L' ) || ( button[ 0 ] == 'M' ) || ( button[ 0 ] == 'R' ) ) && ( button[ 1 ] == 0 ) ) {
                break;
            }
            std::print( "输入错误, 请重新输入: " );
        }
        for ( short i{ 5 }; i >= 0; --i ) {
            std::print( "请在 %d 秒内将鼠标移动到指定位置.\r", i );
            if ( !i ) {
                break;
            }
            Sleep( 1000 );
        }
        puts( "\n正在应用配置." );
        clicker.set( button[ 0 ], click, sleepTime );
        puts( "开始执行." );
        clicker.run();
        puts( "执行完毕.\n" );
    }
    return 0;
}