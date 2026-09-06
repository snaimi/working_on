/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 09:52:55 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODEXION_H
# define CODEXION_H

# include <stdio.h>
# include <stdlib.h>
# include <unistd.h>
# include <pthread.h>
# include <sys/time.h>

# define SCHEDULER_FIFO 0
# define SCHEDULER_EDF  1

typedef struct s_dongle
{
	int				id;
	int				in_use;
	long long		cooldown_until;
	pthread_mutex_t	mutex;
	pthread_cond_t	cond;
}	t_dongle;

typedef struct s_metrics
{
	int			number_of_coders;
	long long	time_to_burnout;
	long long	time_to_compile;
	long long	time_to_debug;
	long long	time_to_refactor;
	long long	dongle_cooldown;
	int			number_of_compiles_required;
	int			scheduler;
}	t_metrics;

typedef struct s_coder
{
	int				id;
	pthread_t		thread;
	long long		last_compile_start;
	int				compiles_done;
	t_dongle		*left_dongle;
	t_dongle		*right_dongle;
	struct s_data	*data;
}	t_coder;

typedef struct s_data
{
	t_metrics		metrics;
	long long		start_time;
	int				simulation_over;
	pthread_mutex_t	state_mutex;
	pthread_mutex_t	write_mutex;
	pthread_t		monitor_thread;
	t_coder			*coders;
	t_dongle		*dongles;
}	t_data;

/* --- FUNCTION PROTOTYPES --- */

/* Parsing (parsing.c) */
int			parse_arguments(int argc, char **argv, t_metrics *metrics);

/* Time & Logging (timing.c / routines.c) */
long long	get_time_ms(void);
void		precise_sleep(long long duration_ms, t_data *data);
void		log_status(t_coder *coder, const char *status);

/* Dongle Operations (dongle.c) */
void		init_dongles(t_data *data);
void		destroy_dongles(t_data *data);
int			take_dongles(t_coder *coder);
void		release_dongles(t_coder *coder);

/* Routines & Threads (routines.c & monitor.c) */
void		*coder_routine(void *arg);
void		*monitor_routine(void *arg);

#endif