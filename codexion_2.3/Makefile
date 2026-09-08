# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/24 03:00:00 by norminette        #+#    #+#              #
#    Updated: 2026/09/06 18:06:38 by snaimi           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME        = codexion

CC          = cc
CFLAGS      = -Wall -Wextra -Werror -pthread

SRCS        = codexion.c \
              parsing.c \
              timing.c \
              dongle.c \
              dongle_acquire.c \
              heap.c \
              heap_peek.c \
              routines.c \
              monitor.c

OBJS        = $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(NAME)

%.o: %.c codexion.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re