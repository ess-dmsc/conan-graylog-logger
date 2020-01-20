#include <graylog_logger/Log.hpp>

int main() {
#ifdef WITH_FMT
  Log::FmtMsg(Log::Severity::Warning, "(FMT) Log message: {}", 42);
#else
  Log::Msg(Log::Severity::Warning, "(Non-FMT) Log message: 42");
#endif
  Log::Flush();
}
