#include <flat_map>
#include <iostream>
#include "cpp_utils/windows_app_tools.hpp"
#include "cpp_utils/windows_console_ui.hpp"
using ui_func_args = cpp_utils::console_ui::func_args;
constexpr auto func_back{ cpp_utils::console_ui::func_back };
constexpr auto func_exit{ cpp_utils::console_ui::func_exit };
enum class mouse_button
{
    left,
    mid,
    right
};
auto click( const mouse_button button )
{
    DWORD flag;
    switch ( button ) {
        case mouse_button::left : flag = MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP; break;
        case mouse_button::mid : flag = MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP; break;
        case mouse_button::right : flag = MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP; break;
        default : std::unreachable();
    }
    mouse_event( flag, 0, 0, 0, 0 );
}
auto clear_istream_buffer( std::istream& stream ) noexcept
{
    stream.clear();
    stream.ignore();
}
const std::flat_map< char, mouse_button > mouse_key_map{
  {'l', mouse_button::left },
  {'m', mouse_button::mid  },
  {'r', mouse_button::right}
};
std::chrono::milliseconds sleep_time{};
mouse_button current_mouse_button;
int click_times{};
int config_cnt{};
auto execute( ui_func_args args ) noexcept
{
    args.parent_ui.set_constraints( true, true );
    using namespace std::chrono_literals;
    for ( auto i{ 5 }; i > 0; --i ) {
        std::print( " (i) 请在 {} 秒内将鼠标移动到指定位置.\r", i );
        std::this_thread::sleep_for( 1s );
    }
    cpp_utils::clear_console_traditional( GetStdHandle( STD_OUTPUT_HANDLE ) );
    std::print( " -> 开始执行." );
    for ( auto _{ 0 }; _ < click_times; ++_ ) {
        click( current_mouse_button );
    }
    return func_back;
}
auto init_if_ok( const ui_func_args& args ) noexcept
{
    if ( ++config_cnt == 3 ) {
        args.parent_ui.edit_text( 0, "                   Auto Clicker\n\n" ).add_back( " > 执行 ", execute );
    }
}
auto set_click_times( ui_func_args args ) noexcept
{
    args.parent_ui.set_constraints( false, true );
    std::print( "请输入点击次数: " );
    while ( true ) {
        std::cin >> click_times;
        clear_istream_buffer( std::cin );
        if ( click_times > 0 ) [[likely]] {
            break;
        }
        std::print( "数据错误, 请重新输入: " );
    }
    init_if_ok( args );
    return func_back;
}
auto set_sleep_time( ui_func_args args ) noexcept
{
    args.parent_ui.set_constraints( false, true );
    std::print( "请输入间隔时间 (单位: 毫秒): " );
    int64_t input;
    while ( true ) {
        std::cin >> input;
        clear_istream_buffer( std::cin );
        if ( input > 0 ) [[likely]] {
            sleep_time = std::chrono::milliseconds{ input };
            break;
        }
        std::print( "数据错误, 请重新输入: " );
    }
    init_if_ok( args );
    return func_back;
}
auto set_button( ui_func_args args ) noexcept
{
    args.parent_ui.set_constraints( false, true );
    std::print( "按下左键 (L), 中键 (M), 还是右键 (R)?\n请输入 (不区分大小写): " );
    std::string tmp;
    while ( true ) {
        std::cin >> tmp;
        clear_istream_buffer( std::cin );
        if ( tmp.size() == 1 && mouse_key_map.contains( tmp.front() | 32 ) ) {
            current_mouse_button = mouse_key_map.at( tmp.front() | 32 );
            break;
        }
        std::print( "请输入错误, 请重新输入: " );
    }
    init_if_ok( args );
    return func_back;
}
auto quit() noexcept
{
    return func_exit;
}
auto relaunch_as_admin() noexcept
{
    cpp_utils::relaunch_as_admin( EXIT_SUCCESS );
    return func_exit;
}
auto main() -> int
{
    const auto current_window_handle{ GetConsoleWindow() };
    const auto std_input_handle{ GetStdHandle( STD_INPUT_HANDLE ) };
    const auto std_output_handle{ GetStdHandle( STD_OUTPUT_HANDLE ) };
    cpp_utils::ignore_current_console_exit_signal( true );
    cpp_utils::enable_window_minimize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_maximize_ctrl( current_window_handle, false );
    cpp_utils::enable_window_close_ctrl( current_window_handle, false );
    cpp_utils::enable_window_menu( current_window_handle, false );
    cpp_utils::set_current_console_charset( 54936 );
    cpp_utils::set_current_console_title( "Auto Clicker" );
    cpp_utils::set_console_size( current_window_handle, std_output_handle, 50, 25 );
    cpp_utils::fix_window_size( current_window_handle, true );
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
      .add_back( " > 设置 点击次数 ", set_click_times )
      .add_back( " > 设置 点击间隔时间 ", set_sleep_time )
      .add_back( " > 设置 点击键 ", set_button )
      .show();
    return EXIT_SUCCESS;
}