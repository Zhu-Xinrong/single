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
    auto set( const char _button, const int _click, const std::chrono::milliseconds _sleep_time )
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
    auto operator=( const auto_click & ) -> auto_click & = default;
    auto operator=( auto_click && ) -> auto_click &      = default;
    auto_click()                                         = default;
    auto_click( const auto_click & )                     = default;
    auto_click( auto_click && )                          = default;
    ~auto_click()                                        = default;
};
constexpr std::chrono::seconds one_seconds{ 1 };
int click{};
char button[ 2 ]{};
std::chrono::milliseconds sleep_time{};
unsigned short config_cnt{};
auto_click clicker;
auto execute( cpp_utils::console_ui::func_args )
{
    clicker.set( button[ 0 ], click, sleep_time );
    for ( short i{ 5 }; i >= 0; --i ) {
        std::print( " (i) 请在 {} 秒内将鼠标移动到指定位置.\r", i );
        std::this_thread::sleep_for( one_seconds );
    }
    std::print( "\n -> 开始执行." );
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
    const auto std_input_handle{ GetStdHandle( STD_INPUT_HANDLE ) };
    const auto std_output_handle{ GetStdHandle( STD_OUTPUT_HANDLE ) };
    cpp_utils::console_ui ui{ std_input_handle, std_output_handle };
    cpp_utils::set_console_title( "Auto Clicker" );
    cpp_utils::set_console_charset( 54936 );
    cpp_utils::set_console_size( current_window_handle, std_output_handle, 50, 25 );
    cpp_utils::fix_window_size( current_window_handle, true );
    cpp_utils::enable_window_minimize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_maximize_ctrl( current_window_handle, false );
    ui.add_back( std::format( "                    Auto Clicker\n\n" ) )
      .add_back( " (i) 全部设置后即可执行.\n" )
      .add_back( " < 退出 ", []( cpp_utils::console_ui::func_args )
    { return cpp_utils::console_ui::exit; }, cpp_utils::console_text::foreground_red | cpp_utils::console_text::foreground_intensity )
      .add_back( " > 设置点击次数 ", set_click_num )
      .add_back( " > 设置点击间隔时间 ", set_sleep_time )
      .add_back( " > 设置点击键 ", set_button )
      .show();
    return 0;
}