#define _CRT_SECURE_NO_WARNINGS
#include "cpp_utils.hpp"
class auto_click final {
  private:
    char button_{};
    int click_{}, counter_{};
    std::chrono::milliseconds sleep_time_{};
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
    auto set( char _button, int _click, std::chrono::milliseconds _sleep_time )
    {
        this->button_     = _button;
        this->click_      = _click;
        this->sleep_time_ = _sleep_time;
    }
    auto run()
    {
        for ( ; counter_ < click_; ++counter_ ) {
            execute_();
            cpp_utils::perf_sleep( sleep_time_ );
        }
    }
};
auto main() -> int
{
    using namespace std::chrono_literals;
    cpp_utils::console_ui_ansi ui;
    auto_click clicker;
    std::chrono::milliseconds sleep_time{};
    int click{};
    char button[ 2 ]{};
    auto set_click_num{ [ & ]( cpp_utils::console_ui_ansi::func_args _arg )
    {
        _arg.parent_ui.lock( false, true );
        std::print( "输入点击次数: " );
        while ( true ) {
            std::scanf( "%d", &click );
            if ( click > 0 ) {
                break;
            }
            std::print( "数据必须大于 0, 请重新输入: " );
        }
        return cpp_utils::console_value::ui_back;
    } };
    auto set_sleep_time{ [ & ]( cpp_utils::console_ui_ansi::func_args _arg )
    {
        _arg.parent_ui.lock( false, true );
        std::print( "输入间隔时间 (单位: 毫秒): " );
        while ( true ) {
            uint64_t tmp;
            std::scanf( "%Lu", &tmp );
            if ( tmp > 0 ) {
                sleep_time = std::chrono::milliseconds{ tmp };
                break;
            }
            std::print( "输入数据必须大于 0, 请重新输入: " );
        }
        return cpp_utils::console_value::ui_back;
    } };
    auto set_button{ [ & ]( cpp_utils::console_ui_ansi::func_args _arg )
    {
        _arg.parent_ui.lock( false, true );
        std::print( "按下左键 (L), 中键 (M), 还是右键 (R): " );
        while ( true ) {
            std::scanf( "%s", button );
            if ( ( ( button[ 0 ] == 'L' ) || ( button[ 0 ] == 'M' ) || ( button[ 0 ] == 'R' ) ) && ( button[ 1 ] == 0 ) ) {
                break;
            }
            std::print( "输入错误, 请重新输入: " );
        }
        return cpp_utils::console_value::ui_back;
    } };
    auto execute{ [ & ]( cpp_utils::console_ui_ansi::func_args _arg )
    {
        clicker.set( button[ 0 ], click, sleep_time );
        for ( short i{ 5 }; i >= 0; --i ) {
            std::print( "请在 {} 秒内将鼠标移动到指定位置.\r", i );
            cpp_utils::perf_sleep( 1s );
        }
        std::print( "\n开始执行." );
        clicker.run();
        return cpp_utils::console_value::ui_back;
    } };
    ui.add_back( std::format( "{}Auto Clicker\n\n", std::string( 19, ' ' ) ) )
      .add_back(
        " < 退出 ", []( cpp_utils::console_ui_ansi::func_args ) { return cpp_utils::console_value::ui_exit; },
        cpp_utils::console_value::text_foreground_red | cpp_utils::console_value::text_foreground_intensity )
      .add_back( " > 设置点击次数 ", set_click_num )
      .add_back( " > 设置点击间隔时间 ", set_sleep_time )
      .add_back( " > 设置点击键 ", set_button )
      .add_back( " > 执行 ", execute )
      .set_console( "Auto Clicker", 54936, 50, 25, true, true, true, 255 )
      .show();
    return 0;
}