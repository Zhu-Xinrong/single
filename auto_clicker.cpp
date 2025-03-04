#define _CRT_SECURE_NO_WARNINGS
#include "cpp_utils.hpp"
class auto_click final {
  private:
    char button_{};
    int click_{};
    int counter_{};
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
            std::this_thread::sleep_for( sleep_time_ );
        }
    }
};
constexpr std::chrono::seconds one_seconds{ 1 };
auto_click clicker;
std::chrono::milliseconds sleep_time{};
int click{};
short config_cnt{};
char button[ 2 ]{};
auto execute( cpp_utils::console_ui::func_args )
{
    clicker.set( button[ 0 ], click, sleep_time );
    for ( short i{ 5 }; i >= 0; --i ) {
        std::print( " (i) 请在 {} 秒内将鼠标移动到指定位置.\r", i );
        std::this_thread::sleep_for( one_seconds );
    }
    std::print( "\n (i) 开始执行." );
    clicker.run();
    return cpp_utils::console_ui::back;
}
auto check( cpp_utils::console_ui::func_args &_arg )
{
    ++config_cnt;
    if ( config_cnt == 3 ) {
        _arg.parent_ui.remove( 1, 2 ).add_back( " > 执行 ", execute );
    }
}
auto set_click_num( cpp_utils::console_ui::func_args _arg )
{
    _arg.parent_ui.lock( false, true );
    std::print( "请输入点击次数: " );
    while ( true ) {
        std::scanf( "%d", &click );
        if ( click > 0 ) {
            break;
        }
        std::print( "数据必须大于 0, 请重新输入: " );
    }
    check( _arg );
    return cpp_utils::console_ui::back;
}
auto set_sleep_time( cpp_utils::console_ui::func_args _arg )
{
    _arg.parent_ui.lock( false, true );
    std::print( "请输入间隔时间 (单位: 毫秒): " );
    while ( true ) {
        uint64_t tmp;
        std::scanf( "%Lu", &tmp );
        if ( tmp > 0 ) {
            sleep_time = std::chrono::milliseconds{ tmp };
            break;
        }
        std::print( "请输入数据必须大于 0, 请重新输入: " );
    }
    check( _arg );
    return cpp_utils::console_ui::back;
}
auto set_button( cpp_utils::console_ui::func_args _arg )
{
    _arg.parent_ui.lock( false, true );
    std::print( "按下左键 (L), 中键 (M), 还是右键 (R): " );
    while ( true ) {
        std::scanf( "%s", button );
        if ( ( button[ 0 ] == 'L' || button[ 0 ] == 'M' || button[ 0 ] == 'R' ) && button[ 1 ] == '\0' ) {
            break;
        }
        std::print( "请输入错误, 请重新输入: " );
    }
    check( _arg );
    return cpp_utils::console_ui::back;
}
auto main() -> int
{
    const auto current_window_handle{ GetConsoleWindow() };
    cpp_utils::console_ui ui;
    cpp_utils::set_console_title( "Auto Clicker" );
    cpp_utils::set_console_charset( 54936 );
    cpp_utils::set_console_size( 50, 25 );
    cpp_utils::fix_window_size( current_window_handle, true );
    cpp_utils::enable_window_minimize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_maximize_ctrl( current_window_handle, false );
    ui.add_back( std::format( "                   Auto Clicker\n\n" ) )
      .add_back( " (i) 全部设置后即可执行.\n" )
      .add_back(
        " < 退出 ", []( cpp_utils::console_ui::func_args ) { return cpp_utils::console_ui::exit; },
        cpp_utils::console_value::text_foreground_red | cpp_utils::console_value::text_foreground_intensity )
      .add_back( " > 设置点击次数 ", set_click_num )
      .add_back( " > 设置点击间隔时间 ", set_sleep_time )
      .add_back( " > 设置点击键 ", set_button )
      .show();
    return 0;
}