#include <graylog_logger/Log.hpp>
#include <iostream>

int main() { Log::Msg(Log::Severity::Warning, "42"); }
