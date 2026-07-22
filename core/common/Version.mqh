//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Version.mqh                                            |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Platform version information and utilities.            |
//+------------------------------------------------------------------+
#ifndef CORE_COMMON_VERSION_MQH
#define CORE_COMMON_VERSION_MQH

class CVersion
{
private:
   int m_major;
   int m_minor;
   int m_patch;

public:

   CVersion()
   {
      m_major = 1;
      m_minor = 0;
      m_patch = 0;
   }

   int Major() const
   {
      return m_major;
   }

   int Minor() const
   {
      return m_minor;
   }

   int Patch() const
   {
      return m_patch;
   }

   string ToString() const
   {
      return StringFormat("%d.%d.%d",
                          m_major,
                          m_minor,
                          m_patch);
   }

   bool Equals(const CVersion &other) const
   {
      return (m_major == other.m_major &&
              m_minor == other.m_minor &&
              m_patch == other.m_patch);
   }

   bool IsCompatible(const CVersion &other) const
   {
      return (m_major == other.m_major);
   }
};

#endif // CORE_COMMON_VERSION_MQH