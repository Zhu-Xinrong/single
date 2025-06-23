#include <iostream>
#include "cpp_utils/windows_app_tools.hpp"
#include "cpp_utils/windows_console_ui.hpp"
constexpr auto func_back{ cpp_utils::console_ui::func_back };
constexpr auto func_exit{ cpp_utils::console_ui::func_exit };
using ui_func_args = cpp_utils::console_ui::func_args;
class auto_click final
{
  private:
    char button_{};
    int click_{};
    std::chrono::milliseconds sleep_time_{};
    auto execute_() noexcept
    {
        DWORD flag;
        switch ( button_ ) {
            case 'L' :
            case 'l' : flag = MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP; break;
            case 'M' :
            case 'm' : flag = MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP; break;
            case 'R' :
            case 'r' : flag = MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP; break;
        }
        mouse_event( flag, 0, 0, 0, 0 );
    }
  public:
    auto set( const char _button, const int _click, const std::chrono::milliseconds _sleep_time ) noexcept
    {
        button_     = _button;
        click_      = _click;
        sleep_time_ = _sleep_time;
    }
    auto run() noexcept
    {
        for ( [[maybe_unused]] const auto _ : std::ranges::iota_view{ decltype( click_ ){ 0 }, click_ } ) {
            execute_();
            std::this_thread::sleep_for( sleep_time_ );
        }
    }
    auto operator=( const auto_click& ) noexcept -> auto_click& = default;
    auto operator=( auto_click&& ) noexcept -> auto_click&      = default;
    auto_click() noexcept                                       = default;
    auto_click( const auto_click& ) noexcept                    = default;
    auto_click( auto_click&& ) noexcept                         = default;
    ~auto_click() noexcept                                      = default;
};
const auto current_window_handle{ GetConsoleWindow() };
const auto std_input_handle{ GetStdHandle( STD_INPUT_HANDLE ) };
const auto std_output_handle{ GetStdHandle( STD_OUTPUT_HANDLE ) };
auto_click clicker;
std::chrono::milliseconds sleep_time{};
int click{};
char button[ 2 ]{};
unsigned short config_cnt{};
auto clear_cin_buffer() noexcept
{
    std::cin.clear();
    std::cin.ignore();
}
auto execute( ui_func_args args ) noexcept
{
    constexpr std::chrono::seconds one_seconds{ 1 };
    args.parent_ui.set_limits( true, true );
    clicker.set( button[ 0 ], click, sleep_time );
    for ( const auto i : std::ranges::iota_view{ 0, 5 } ) {
        std::print( " (i) 请在 {} 秒内将鼠标移动到指定位置.\r", 5 - i );
        std::this_thread::sleep_for( one_seconds );
    }
    cpp_utils::clear_console( std_output_handle );
    std::print( " -> 开始执行." );
    clicker.run();
    return func_back;
}
auto check( ui_func_args& args ) noexcept
{
    ++config_cnt;
    if ( config_cnt == 3 ) {
        args.parent_ui.edit_text( 0, "                   Auto Clicker\n\n" ).add_back( " > 执行 ", execute );
    }
}
auto set_click_num( ui_func_args args ) noexcept
{
    args.parent_ui.set_limits( false, true );
    std::print( "请输入点击次数: " );
    while ( true ) {
        std::cin >> click;
        clear_cin_buffer();
        if ( click > 0 ) [[unlikely]] {
            break;
        }
        std::print( "数据必须大于 0, 请重新输入: " );
    }
    check( args );
    return func_back;
}
auto set_sleep_time( ui_func_args args ) noexcept
{
    args.parent_ui.set_limits( false, true );
    std::print( "请输入间隔时间 (单位: 毫秒): " );
    while ( true ) {
        int64_t tmp;
        std::cin >> tmp;
        clear_cin_buffer();
        if ( tmp > 0 ) [[unlikely]] {
            sleep_time = std::chrono::milliseconds{ tmp };
            break;
        }
        std::print( "数据必须大于 0, 请重新输入: " );
    }
    check( args );
    return func_back;
}
auto set_button( ui_func_args args ) noexcept
{
    args.parent_ui.set_limits( false, true );
    std::print( "按下左键 (L), 中键 (M), 还是右键 (R)?\n请输入 (不区分大小写): " );
    bool is_ok{ false };
    while ( !is_ok ) {
        std::cin >> button;
        clear_cin_buffer();
        switch ( button[ 0 ] ) {
            case 'L' :
            case 'l' :
            case 'M' :
            case 'm' :
            case 'R' :
            case 'r' : is_ok = true; break;
            default : std::print( "请输入错误, 请重新输入: " );
        }
    }
    check( args );
    return func_back;
}
auto quit( ui_func_args ) noexcept
{
    return func_exit;
}
auto relaunch_as_admin( ui_func_args ) noexcept
{
    cpp_utils::relaunch_as_admin( EXIT_SUCCESS );
    return func_exit;
}
auto main() -> int
{
    cpp_utils::ignore_current_console_exit_signal( true );
    cpp_utils::enable_window_minimize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_maximize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_close_ctrl( current_window_handle, false );
    cpp_utils::enable_window_menu( current_window_handle, false );
    cpp_utils::set_current_console_charset( 54936 );
    cpp_utils::set_current_console_title( "Auto Clicker" );
    cpp_utils::set_console_size( current_window_handle, std_output_handle, 50, 25 );
    cpp_utils::fix_window_size( current_window_handle, true );
    std::ios::sync_with_stdio( false );
    cpp_utils::console_ui ui{ std_input_handle, std_output_handle };
    ui.add_back(
        "                   Auto Clicker\n\n\n"
        " (i) 全部设置后即可执行.\n" )
      .add_back( " < 退出 ", quit, cpp_utils::console_text::foreground_red | cpp_utils::console_text::foreground_intensity );
    if ( !cpp_utils::is_run_as_admin() ) {
        ui.add_back(
          " < 以管理员权限重启 ", relaunch_as_admin,
          cpp_utils::console_text::foreground_green | cpp_utils::console_text::foreground_intensity );
    }
    ui.add_back( "" )
      .add_back( " > 设置 点击次数 ", set_click_num )
      .add_back( " > 设置 点击间隔时间 ", set_sleep_time )
      .add_back( " > 设置 点击键 ", set_button )
      .show();
    return EXIT_SUCCESS;
}