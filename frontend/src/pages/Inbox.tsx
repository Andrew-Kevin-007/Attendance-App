import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import { Inbox as InboxIcon, Mail, MailOpen, Trash2, CheckCheck, Loader2, Bell, AlertCircle, CheckCircle, Info } from "lucide-react";
import { notificationsAPI } from "@/lib/api";

const Inbox = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const data = await notificationsAPI.getAll();
      setNotifications(data);
    } catch (err: any) {
      setError(err.message || "Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await notificationsAPI.markAsRead(id);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, read: true } : n
      ));
    } catch (err: any) {
      // Silent fail - notification state will update on next fetch
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead();
      setNotifications(notifications.map(n => ({ ...n, read: true })));
    } catch (err: any) {
      // Silent fail
    }
  };

  const deleteNotification = async (id: number) => {
    try {
      await notificationsAPI.delete(id);
      setNotifications(notifications.filter(n => n.id !== id));
    } catch (err: any) {
      // Silent fail
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "warning":
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getNotificationBgColor = (type: string, read: boolean) => {
    const opacity = read ? "5" : "10";
    switch (type) {
      case "success":
        return `bg-green-500/${opacity}`;
      case "warning":
        return `bg-yellow-500/${opacity}`;
      case "error":
        return `bg-red-500/${opacity}`;
      default:
        return `bg-blue-500/${opacity}`;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-12">
        {/* Hero */}
        <section className="section-apple border-b border-divider">
          <div className="container-apple">
            <div className="max-w-3xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 mb-4 opacity-0 animate-fade-in">
                <InboxIcon className="w-8 h-8" />
              </div>
              <h1 className="headline-large mb-4 opacity-0 animate-fade-in-up">
                Inbox
              </h1>
              <p className="subhead opacity-0 animate-fade-in-up delay-100">
                {unreadCount > 0 ? `${unreadCount} unread message${unreadCount !== 1 ? 's' : ''}` : 'All caught up'}
              </p>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="btn-apple mt-6 opacity-0 animate-fade-in-up delay-200"
                >
                  <CheckCheck className="w-5 h-5" />
                  Mark All as Read
                </button>
              )}
            </div>
          </div>
        </section>

        {/* Notifications List */}
        <section className="section-apple">
          <div className="container-apple">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            ) : error ? (
              <div className="text-center py-20">
                <p className="text-destructive">{error}</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center py-20">
                <Mail className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-xl font-semibold mb-2">No messages yet</h3>
                <p className="text-muted-foreground">
                  Your inbox is empty. Notifications will appear here.
                </p>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto space-y-2">
                {notifications.map((notification, index) => (
                  <div
                    key={notification.id}
                    className={`card-apple p-4 opacity-0 animate-fade-in-up ${getNotificationBgColor(notification.type, notification.read)} ${!notification.read ? 'border-l-4 border-primary' : ''}`}
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h3 className={`font-semibold ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                            {notification.title}
                          </h3>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {formatDate(notification.created_at)}
                          </span>
                        </div>
                        <p className={`text-sm ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {notification.message}
                        </p>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {!notification.read && (
                          <button
                            onClick={() => markAsRead(notification.id)}
                            className="p-2 hover:bg-accent rounded-lg transition-colors"
                            title="Mark as read"
                          >
                            <MailOpen className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => deleteNotification(notification.id)}
                          className="p-2 hover:bg-destructive/10 text-destructive rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Inbox;
