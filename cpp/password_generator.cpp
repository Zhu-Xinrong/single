#include <numeric>
#include <print>
#include <random>
#include <ranges>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
auto make_password( const std::size_t length, const std::vector< char >& dic )
{
    std::string password( length, '\0' );
    std::mt19937_64 rng{ std::random_device{}() };
    std::uniform_int_distribution< std::size_t > dist( 0, dic.size() - 1 );
    for ( auto& e : password ) {
        e = dic[ dist( rng ) ];
    }
    return password;
}
auto show_help_info() noexcept
{
    std::print(
      "[ Password Generator ]\n"
      "Supported arguments:\n"
      "  '--no-capital-letters': Remove capital letters from the dictionary.\n"
      "  '--no-lowercase-letters': Remove lowercase letters from the dictionary.\n"
      "  '--no-numbers': Remove numbers from the dictionary.\n"
      "  '--no-special-characters': Remove special characters from the dictionary.\n"
      "  '--password-length=[a positive integer]': Set the length of a single password.\n"
      "  '--number-of-passwords=[a positive integer]': Set the number of passwords to generate.\n"
      "NOTE: The dictionary cannot be empty!\n" );
}
auto main( const int argc, const char* const args[] ) -> int
{
    constexpr auto error_info{ "Arguments failed! Please use '--help' to view the usage guide.\n" };
    std::unordered_map< std::string_view, bool > options{
      {"--no-capital-letters",    false},
      {"--no-lowercase-letters",  false},
      {"--no-numbers",            false},
      {"--no-special-characters", false}
    };
    std::unordered_map< std::string_view, long long > settings{
      {"--password-length=",     16},
      {"--number-of-passwords=", 1 }
    };
    for ( int i{ 1 }; i < argc; ++i ) {
        const std::string_view current_args{ args[ i ] };
        if ( current_args == "--help" ) {
            show_help_info();
            return EXIT_SUCCESS;
        }
        if ( options.contains( current_args ) ) {
            options[ current_args ] = true;
            continue;
        }
        const std::string_view settings_name{ current_args.begin(), std::ranges::find( current_args, '=' ) + 1 };
        if ( settings.contains( settings_name ) ) {
            settings[ settings_name ] = std::stoll( std::ranges::find( current_args, '=' ) + 1 );
            continue;
        }
        std::print( error_info );
        return EXIT_FAILURE;
    }
    std::vector< char > dic;
    if ( !options[ "--no-capital-letters" ] ) {
        for ( const auto c : std::ranges::iota_view{ 'A', 'Z' + 1 } ) {
            dic.emplace_back( c );
        }
    }
    if ( !options[ "--no-lowercase-letters" ] ) {
        for ( const auto c : std::ranges::iota_view{ 'a', 'z' + 1 } ) {
            dic.emplace_back( c );
        }
    }
    if ( !options[ "--no-numbers" ] ) {
        for ( const auto c : std::ranges::iota_view{ '1', '9' + 1 } ) {
            dic.emplace_back( c );
        }
    }
    if ( !options[ "--no-special-characters" ] ) {
        for ( const auto c : R"(!"#$%&'()*+,-./:;<=>?@[\]^_`{|})" ) {
            dic.emplace_back( c );
        }
        dic.pop_back();
    }
    const auto password_length{ settings[ "--password-length=" ] };
    const auto num_of_passwords{ settings[ "--number-of-passwords=" ] };
    if ( num_of_passwords <= 0 || password_length <= 0 || dic.size() == 0 ) {
        std::print( error_info );
        return EXIT_FAILURE;
    }
    for ( std::remove_const_t< decltype( num_of_passwords ) > _{ 0 }; _ < num_of_passwords; ++_ ) {
        std::print( "{}\n", make_password( password_length, dic ) );
    }
    return EXIT_SUCCESS;
}